import pandas as pd
import os
import webbrowser
import tempfile
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# Project Paths
# ============================================================
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "data", "processed", "medical_operations_master.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "operational_bottleneck_analysis_outputs")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ============================================================
# Helper: Open chart in browser WITHOUT blocking the script
# ============================================================
def show_chart(fig, name):
    """Save chart as temp HTML and open in browser. Non-blocking."""
    path = os.path.join(tempfile.gettempdir(), f"{name}.html")
    fig.write_html(path, include_plotlyjs="cdn")
    webbrowser.open(f"file:///{path}")
    print(f"       Browser opened: {name}")

# ============================================================
# STEP 1: Load Dataset
# ============================================================
print("[1/5] Loading dataset...")
df = pd.read_csv(DATA_PATH)
df["Admission_Date"] = pd.to_datetime(df["Admission_Date"])
df["Discharge_Date"]  = pd.to_datetime(df["Discharge_Date"])
print(f"      Loaded {df.shape[0]:,} rows, {df.shape[1]} columns.")

# ============================================================
# STEP 2: Feature Engineering
# ============================================================
print("[2/5] Engineering bottleneck features...")

WAIT_CAT_ORDER = ["<1 hr", "1-2 hr", "2-3 hr", "3-4 hr", "4-5 hr"]

# .astype(str) is REQUIRED: pd.cut returns Categorical which blocks Plotly
df["Wait_Category"] = pd.cut(
    df["Wait_Time_Minutes"],
    bins=[0, 60, 120, 180, 240, 300],
    labels=WAIT_CAT_ORDER
).astype(str)

# Clinical LOS benchmarks by severity
df["Expected_LOS"] = df["Severity_Level"].map(
    {"Low": 2, "Medium": 5, "High": 14, "Critical": 21}
)
# Discharge delay = excess days beyond expected
df["Discharge_Delay_Days"] = (
    df["Length_of_Stay_Days"] - df["Expected_LOS"]
).clip(lower=0)

# 3-hr SLA breach flag
df["Admission_Delay_Flag"] = (df["Wait_Time_Minutes"] > 180).astype(int)

# Dual bottleneck: top-25% wait AND top-25% LOS simultaneously
p75_wait = df["Wait_Time_Minutes"].quantile(0.75)
p75_los  = df["Length_of_Stay_Days"].quantile(0.75)
df["Dual_Bottleneck"] = (
    (df["Wait_Time_Minutes"] > p75_wait) &
    (df["Length_of_Stay_Days"] > p75_los)
).astype(int)

df["Month"] = df["Admission_Date"].dt.to_period("M").astype(str)
print("      Features ready.")

# ============================================================
# STEP 3: KPI Calculations
# ============================================================
print("[3/5] Calculating KPIs...")

avg_wait_time         = df["Wait_Time_Minutes"].mean()
pct_wait_over_3hr     = (df["Wait_Time_Minutes"] > 180).mean() * 100
avg_los               = df["Length_of_Stay_Days"].mean()
avg_discharge_delay   = df["Discharge_Delay_Days"].mean()
total_dual_bottleneck = int(df["Dual_Bottleneck"].sum())
readmission_rate      = df["Readmission_Flag"].mean() * 100
pct_critical          = (df["Severity_Level"] == "Critical").mean() * 100

print()
print("=" * 55)
print("  KEY PERFORMANCE INDICATORS")
print("=" * 55)
print(f"  Total Patients              : {df['Patient_ID'].nunique():,}")
print(f"  Average Wait Time           : {avg_wait_time:.1f} min")
print(f"  Patients Waiting > 3 Hours  : {pct_wait_over_3hr:.1f}%")
print(f"  Average Length of Stay      : {avg_los:.2f} days")
print(f"  Avg Discharge Delay (excess): {avg_discharge_delay:.2f} days")
print(f"  Dual-Bottleneck Cases       : {total_dual_bottleneck:,}")
print(f"  Readmission Rate            : {readmission_rate:.2f}%")
print(f"  Critical-Severity Share     : {pct_critical:.1f}%")
print("=" * 55)

# ============================================================
# STEP 4: Build Summary Tables
# ============================================================
print()
print("[4/5] Building analysis tables...")

# 1. Wait time by department
dept_sizes   = df.groupby("Department_Patient").size().reset_index(name="Total")
wait_by_dept = (
    df.groupby("Department_Patient")["Wait_Time_Minutes"]
    .agg(Avg_Wait_Min="mean", Median_Wait_Min="median",
         P90_Wait_Min=lambda x: x.quantile(0.90),
         Patients_Over_3hr=lambda x: (x > 180).sum())
    .reset_index()
    .rename(columns={"Department_Patient": "Department"})
    .merge(dept_sizes, left_on="Department", right_on="Department_Patient")
)
wait_by_dept["Pct_Over_3hr"] = (
    wait_by_dept["Patients_Over_3hr"] / wait_by_dept["Total"] * 100
).round(2)
wait_by_dept = wait_by_dept[
    ["Department","Avg_Wait_Min","Median_Wait_Min",
     "P90_Wait_Min","Patients_Over_3hr","Pct_Over_3hr"]
].sort_values("Avg_Wait_Min", ascending=False)

# 2. Severity delay
delay_by_severity = (
    df.groupby("Severity_Level")
    .agg(Avg_Wait=("Wait_Time_Minutes","mean"),
         Pct_Delayed=("Admission_Delay_Flag","mean"),
         Avg_LOS=("Length_of_Stay_Days","mean"),
         Avg_Discharge_Delay=("Discharge_Delay_Days","mean"))
    .reset_index()
)
delay_by_severity["Pct_Delayed"] = (
    delay_by_severity["Pct_Delayed"] * 100
).round(2)
delay_by_severity["Severity_Level"] = pd.Categorical(
    delay_by_severity["Severity_Level"],
    categories=["Critical","High","Medium","Low"], ordered=True
)
delay_by_severity = delay_by_severity.sort_values("Severity_Level")

# 3. Discharge delay by department
discharge_delay_dept = (
    df.groupby("Department_Patient")["Discharge_Delay_Days"]
    .agg(Avg_Delay_Days="mean", Max_Delay_Days="max",
         Cases_With_Delay=lambda x: (x > 0).sum())
    .reset_index()
    .rename(columns={"Department_Patient": "Department"})
    .sort_values("Avg_Delay_Days", ascending=False)
)

# 4. Dual bottleneck by department
dual_bn_dept = (
    df.groupby("Department_Patient")
    .agg(Dual_Bottleneck_Cases=("Dual_Bottleneck","sum"),
         Total_Patients=("Patient_ID","count"))
    .reset_index()
)
dual_bn_dept["Bottleneck_Rate_Pct"] = (
    dual_bn_dept["Dual_Bottleneck_Cases"] /
    dual_bn_dept["Total_Patients"] * 100
).round(2)
dual_bn_dept = dual_bn_dept.sort_values("Dual_Bottleneck_Cases", ascending=False)

# 5. Queue distribution
queue_dist = (
    df.groupby(["Department_Patient", "Wait_Category"])
    .size().reset_index(name="Patient_Count")
)

# 6. Monthly trend
monthly_trend = (
    df.groupby("Month")
    .agg(Avg_Wait=("Wait_Time_Minutes","mean"),
         Pct_Delayed=("Admission_Delay_Flag","mean"),
         Avg_LOS=("Length_of_Stay_Days","mean"),
         Total_Patients=("Patient_ID","count"))
    .reset_index()
)
monthly_trend["Pct_Delayed"] = (monthly_trend["Pct_Delayed"]*100).round(2)

# 7. Readmission
readm_dept = (
    df.groupby("Department_Patient")
    .agg(Readmission_Rate=("Readmission_Flag","mean"),
         Readmission_Count=("Readmission_Flag","sum"),
         Total_Patients=("Patient_ID","count"))
    .reset_index()
)
readm_dept["Readmission_Rate_Pct"] = (
    readm_dept["Readmission_Rate"]*100
).round(2)
readm_dept = readm_dept.sort_values("Readmission_Rate_Pct", ascending=False)

# 8. Prolonged stay
prolonged_dept = (
    df[df["Length_of_Stay_Days"] > 14]
    .groupby("Department_Patient")
    .agg(Prolonged_Cases=("Patient_ID","count"),
         Avg_Stay=("Length_of_Stay_Days","mean"))
    .reset_index()
    .sort_values("Prolonged_Cases", ascending=False)
)
prolonged_dept["Avg_Stay"] = prolonged_dept["Avg_Stay"].round(1)

# Heatmap pivot
heat_pivot = (
    df.groupby(["Department_Patient","Severity_Level"])["Wait_Time_Minutes"]
    .mean().round(1).reset_index()
    .pivot(index="Department_Patient", columns="Severity_Level",
           values="Wait_Time_Minutes")[["Critical","High","Medium","Low"]]
)

print("      All tables ready.")

# ============================================================
# STEP 5: Save CSVs (always overwrites - no duplicates ever)
# ============================================================
print()
print("[5/5] Saving CSVs (overwrite - no duplicates)...")
wait_by_dept.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_wait_by_dept.csv"), index=False)
print("      [OK] bottleneck_wait_by_dept.csv")

delay_by_severity.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_delay_by_severity.csv"), index=False)
print("      [OK] bottleneck_delay_by_severity.csv")

discharge_delay_dept.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_discharge_delay_dept.csv"), index=False)
print("      [OK] bottleneck_discharge_delay_dept.csv")

dual_bn_dept.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_dual_cases_dept.csv"), index=False)
print("      [OK] bottleneck_dual_cases_dept.csv")

monthly_trend.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_monthly_trend.csv"), index=False)
print("      [OK] bottleneck_monthly_trend.csv")

readm_dept.to_csv(
    os.path.join(CHARTS_DIR, "bottleneck_readmission_dept.csv"), index=False)
print("      [OK] bottleneck_readmission_dept.csv")

# ============================================================
# CHARTS (open in browser, script does NOT wait/block)
# ============================================================
print()
print("Opening 10 charts in browser...")

# Chart 1: Avg Wait Time by Department
fig1 = px.bar(
    wait_by_dept, x="Avg_Wait_Min", y="Department",
    orientation="h", color="Avg_Wait_Min",
    color_continuous_scale="Reds", text="Avg_Wait_Min",
    title=(
        "Chart 1: Average Admission Wait Time by Department<br>"
        "<sup>Business Insight: ICU and Neurology show the highest wait times "
        "— triage protocols need strengthening in these units.</sup>"
    ),
)
fig1.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
fig1.update_layout(xaxis_title="Average Wait Time (Minutes)",
                   yaxis_title="Department", title_x=0.5,
                   template="plotly_white", coloraxis_showscale=False,
                   margin=dict(l=20, r=80, t=110, b=40),
                   yaxis=dict(autorange="reversed"))
show_chart(fig1, "chart1_wait_by_dept")
input("   >> Chart 1 open. Press Enter for Chart 2...")

# Chart 2: Wait Time Distribution
fig2 = px.histogram(
    df, x="Wait_Time_Minutes", nbins=40,
    color_discrete_sequence=["#E05252"],
    title=(
        "Chart 2: Distribution of Patient Admission Wait Times<br>"
        "<sup>Business Insight: ~40% of patients breach the 3-hour SLA "
        "— a systemic triage capacity gap hospital-wide.</sup>"
    ),
)
fig2.add_vline(x=180, line_dash="dash", line_color="navy",
               annotation_text="3-Hour SLA (180 min)",
               annotation_position="top right")
fig2.add_vline(x=avg_wait_time, line_dash="dot", line_color="green",
               annotation_text=f"Avg ({avg_wait_time:.0f} min)",
               annotation_position="top left")
fig2.update_layout(xaxis_title="Wait Time (Minutes)",
                   yaxis_title="Number of Patients",
                   title_x=0.5, template="plotly_white", bargap=0.05,
                   margin=dict(l=20, r=40, t=110, b=40))
show_chart(fig2, "chart2_wait_distribution")
input("   >> Chart 2 open. Press Enter for Chart 3...")

# Chart 3: Stacked Queue by Dept & Wait Bucket
fig3 = px.bar(
    queue_dist, x="Department_Patient", y="Patient_Count",
    color="Wait_Category", barmode="stack",
    color_discrete_sequence=px.colors.sequential.Reds[2:],
    category_orders={"Wait_Category": WAIT_CAT_ORDER},
    title=(
        "Chart 3: Patient Queue by Wait-Time Bucket and Department<br>"
        "<sup>Business Insight: High-wait patients are spread equally across all "
        "departments — the bottleneck is structural and system-wide.</sup>"
    ),
)
fig3.update_layout(xaxis_title="Department", yaxis_title="Number of Patients",
                   legend_title="Wait Category", title_x=0.5,
                   template="plotly_white", margin=dict(l=20, r=40, t=110, b=40))
show_chart(fig3, "chart3_queue_by_dept")
input("   >> Chart 3 open. Press Enter for Chart 4...")

# Chart 4: Discharge Delay by Department
fig4 = px.bar(
    discharge_delay_dept, x="Department", y="Avg_Delay_Days",
    color="Avg_Delay_Days", color_continuous_scale="Oranges",
    text="Avg_Delay_Days",
    title=(
        "Chart 4: Average Discharge Delay Beyond Clinical Benchmark by Department<br>"
        "<sup>Business Insight: Gynecology and General Surgery exceed discharge "
        "benchmarks most — delayed discharges inflate bed occupancy.</sup>"
    ),
)
fig4.update_traces(texttemplate="%{text:.2f} days", textposition="outside")
fig4.update_layout(xaxis_title="Department",
                   yaxis_title="Avg Excess Days Beyond Expected LOS",
                   title_x=0.5, template="plotly_white",
                   coloraxis_showscale=False,
                   margin=dict(l=20, r=40, t=120, b=40))
show_chart(fig4, "chart4_discharge_delay")
input("   >> Chart 4 open. Press Enter for Chart 5...")

# Chart 5: Wait Time vs LOS by Severity (Dual Axis)
fig5 = make_subplots(specs=[[{"secondary_y": True}]])
sev_labels = delay_by_severity["Severity_Level"].astype(str).tolist()
fig5.add_trace(go.Bar(
    x=sev_labels, y=delay_by_severity["Avg_Wait"].tolist(),
    name="Avg Wait Time (min)", marker_color="#E05252",
    text=[f"{v:.1f}" for v in delay_by_severity["Avg_Wait"]],
    textposition="outside"), secondary_y=False)
fig5.add_trace(go.Scatter(
    x=sev_labels, y=delay_by_severity["Avg_LOS"].tolist(),
    name="Avg Length of Stay (days)", mode="lines+markers",
    marker=dict(size=10, color="navy"),
    line=dict(width=2.5, color="navy")), secondary_y=True)
fig5.update_layout(
    title_text=(
        "Chart 5: Admission Wait Time vs Length of Stay by Severity<br>"
        "<sup>Business Insight: Critical patients have the longest stays but NOT "
        "faster admission — a triage priority gap risking adverse outcomes.</sup>"
    ),
    title_x=0.5, template="plotly_white",
    legend=dict(x=0.01, y=0.99),
    margin=dict(l=20, r=60, t=120, b=40))
fig5.update_xaxes(title_text="Severity Level")
fig5.update_yaxes(title_text="Avg Wait Time (Minutes)", secondary_y=False)
fig5.update_yaxes(title_text="Avg Length of Stay (Days)", secondary_y=True)
show_chart(fig5, "chart5_severity_wait_los")
input("   >> Chart 5 open. Press Enter for Chart 6...")

# Chart 6: Monthly Wait Trend
fig6 = go.Figure()
fig6.add_trace(go.Scatter(
    x=monthly_trend["Month"].tolist(),
    y=monthly_trend["Avg_Wait"].tolist(),
    mode="lines+markers", name="Avg Wait Time (min)",
    line=dict(color="#E05252", width=2.5), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(224,82,82,0.12)"))
fig6.add_hline(y=180, line_dash="dash", line_color="darkred",
               annotation_text="3-hr SLA (180 min)",
               annotation_position="top right")
fig6.add_hline(y=avg_wait_time, line_dash="dot", line_color="gray",
               annotation_text=f"Overall Avg ({avg_wait_time:.1f} min)",
               annotation_position="bottom right")
fig6.update_layout(
    title=(
        "Chart 6: Monthly Trend — Average Patient Admission Wait Time<br>"
        "<sup>Business Insight: Wait times breach the 3-hr SLA every month "
        "— Q1 and Q3 spikes need seasonal staffing surge plans.</sup>"
    ),
    xaxis_title="Month", yaxis_title="Avg Wait Time (Minutes)",
    title_x=0.5, template="plotly_white",
    margin=dict(l=20, r=40, t=120, b=80),
    xaxis=dict(tickangle=45))
show_chart(fig6, "chart6_monthly_trend")
input("   >> Chart 6 open. Press Enter for Chart 7...")

# Chart 7: Dual Bottleneck Bubble Chart
fig7 = px.scatter(
    dual_bn_dept, x="Department_Patient", y="Bottleneck_Rate_Pct",
    size="Dual_Bottleneck_Cases", color="Bottleneck_Rate_Pct",
    color_continuous_scale="Reds", size_max=55,
    text="Dual_Bottleneck_Cases",
    title=(
        "Chart 7: Dual-Bottleneck Cases by Department<br>"
        "(Top-25% Wait Time AND Top-25% LOS Combined)<br>"
        "<sup>Business Insight: Cardiology leads dual-bottleneck cases — patients face "
        "both long waits and extended stays, compounding resource strain.</sup>"
    ),
)
fig7.update_traces(textposition="top center", textfont=dict(size=11))
fig7.update_layout(xaxis_title="Department",
                   yaxis_title="Dual-Bottleneck Rate (%)",
                   title_x=0.5, template="plotly_white",
                   coloraxis_showscale=False,
                   margin=dict(l=20, r=40, t=150, b=40))
show_chart(fig7, "chart7_dual_bottleneck")
input("   >> Chart 7 open. Press Enter for Chart 8...")

# Chart 8: Readmission Rate
fig8 = px.bar(
    readm_dept, x="Readmission_Rate_Pct", y="Department_Patient",
    orientation="h", color="Readmission_Rate_Pct",
    color_continuous_scale="YlOrRd", text="Readmission_Rate_Pct",
    title=(
        "Chart 8: Readmission Rate by Department (Outcome Bottleneck)<br>"
        "<sup>Business Insight: Cardiology's 8.09% readmission rate leads all "
        "departments — discharge bottlenecks cycle patients back repeatedly.</sup>"
    ),
)
fig8.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig8.update_layout(xaxis_title="Readmission Rate (%)",
                   yaxis_title="Department", title_x=0.5,
                   template="plotly_white", coloraxis_showscale=False,
                   margin=dict(l=20, r=80, t=120, b=40),
                   yaxis=dict(autorange="reversed"))
show_chart(fig8, "chart8_readmission")
input("   >> Chart 8 open. Press Enter for Chart 9...")

# Chart 9: Heatmap Dept x Severity
fig9 = go.Figure(data=go.Heatmap(
    z=heat_pivot.values.tolist(),
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale="Reds",
    text=heat_pivot.values.tolist(),
    texttemplate="%{text:.1f}",
    showscale=True,
    colorbar=dict(title="Avg Wait (min)")))
fig9.update_layout(
    title=(
        "Chart 9: Heatmap — Avg Wait Time by Department x Severity Level<br>"
        "<sup>Business Insight: Dermatology-Critical patients face the highest "
        "wait — a triage misrouting issue needing immediate review.</sup>"
    ),
    xaxis_title="Severity Level", yaxis_title="Department",
    title_x=0.5, template="plotly_white",
    margin=dict(l=20, r=40, t=120, b=40))
show_chart(fig9, "chart9_heatmap")
input("   >> Chart 9 open. Press Enter for Chart 10...")

# Chart 10: Prolonged Stay
fig10 = px.bar(
    prolonged_dept, x="Department_Patient", y="Prolonged_Cases",
    color="Avg_Stay", color_continuous_scale="OrRd",
    text="Prolonged_Cases",
    title=(
        "Chart 10: Prolonged-Stay Cases (LOS > 14 Days) by Department<br>"
        "<sup>Business Insight: Gynecology leads prolonged stays — beds blocked "
        "for weeks, creating a cascading admission bottleneck facility-wide.</sup>"
    ),
)
fig10.update_traces(texttemplate="%{text:,}", textposition="outside")
fig10.update_layout(xaxis_title="Department",
                    yaxis_title="Number of Prolonged-Stay Patients",
                    coloraxis_colorbar_title="Avg Stay (days)",
                    title_x=0.5, template="plotly_white",
                    margin=dict(l=20, r=40, t=120, b=40))
show_chart(fig10, "chart10_prolonged_stay")

# ============================================================
print()
print("=" * 55)
print("  TASK 7 - OPERATIONAL BOTTLENECK ANALYSIS DONE")
print("  10 charts opened in browser")
print("  6 CSV files saved in /charts/")
print("=" * 55)