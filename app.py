import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าเว็บ Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Waste Management Dashboard", page_icon="♻️", layout="wide"
)


# ---------------------------------------------------------
# 2. ฟังก์ชันโหลดข้อมูลจาก CSV (รองรับไฟล์จาก data.go.th)
# ---------------------------------------------------------
@st.cache_data
def load_data():
  file_name = "waste_data.csv"

  # อ่านไฟล์ CSV (รองรับ Encoding ภาษาไทยทั้ง UTF-8 และ TIS-620 / CP874)
  df = None
  encodings = ["utf-8", "tis-620", "cp874", "utf-8-sig"]

  for enc in encodings:
    try:
      df = pd.read_csv(file_name, encoding=enc)
      break
    except Exception:
      continue

  # กรณีไม่มีไฟล์ CSV ใน GitHub ให้ใช้ Mock Data เผื่อไว้เว็บจะได้ไม่ crash
  if df is None:
    data = {
        "ปี": [2568] * 12 + [2569] * 12,
        "สังกัด": ["ส่วนกลาง"] * 12 + ["ส่วนภูมิภาค"] * 12,
        "หน่วยงาน": ["กองการต่างประเทศ"] * 12 + ["กลุ่มงานจริยธรรม"] * 12,
        "เดือน": [
            "มกราคม",
            "กุมภาพันธ์",
            "มีนาคม",
            "เมษายน",
            "พฤษภาคม",
            "มิถุนายน",
            "กรกฎาคม",
            "สิงหาคม",
            "กันยายน",
            "ตุลาคม",
            "พฤศจิกายน",
            "ธันวาคม",
        ]
        * 2,
        "ขยะที่เกิดขึ้น (กก.)": [
            9800,
            8500,
            8200,
            7800,
            7500,
            300,
            310,
            320,
            300,
            310,
            320,
            330,
        ]
        * 2,
        "นำไปใช้ประโยชน์ (กก.)": [
            2000,
            2100,
            2050,
            1900,
            1800,
            50,
            55,
            60,
            50,
            55,
            60,
            65,
        ]
        * 2,
        "ขยะที่ส่งกำจัด (กก.)": [
            6200,
            5600,
            5200,
            4800,
            4500,
            200,
            210,
            220,
            200,
            210,
            220,
            230,
        ]
        * 2,
        "โฟมบรรจุอาหาร (ใบ)": [0] * 24,
    }
    df = pd.DataFrame(data)

  # ทำความสะอาดและแปลงชื่อคอลัมน์ให้ตรงกัน
  col_mapping = {}
  for col in df.columns:
    c_str = str(col).strip()
    if "ปี" in c_str:
      col_mapping[col] = "ปี"
    elif "สังกัด" in c_str:
      col_mapping[col] = "สังกัด"
    elif "หน่วยงาน" in c_str:
      col_mapping[col] = "หน่วยงาน"
    elif "เดือน" in c_str:
      col_mapping[col] = "เดือน"
    elif "เกิดขึ้น" in c_str:
      col_mapping[col] = "ขยะที่เกิดขึ้น (กก.)"
    elif "ประโยชน์" in c_str:
      col_mapping[col] = "นำไปใช้ประโยชน์ (กก.)"
    elif "กำจัด" in c_str:
      col_mapping[col] = "ขยะที่ส่งกำจัด (กก.)"
    elif "โฟม" in c_str:
      col_mapping[col] = "โฟมบรรจุอาหาร (ใบ)"

  df = df.rename(columns=col_mapping)
  return df


df_raw = load_data()

# ---------------------------------------------------------
# 3. Sidebar Filter (Interactive Widgets)
# ---------------------------------------------------------
st.sidebar.title("⚙️ Filter ข้อมูล")

# Filter: ปี
if "ปี" in df_raw.columns:
  all_years = sorted(df_raw["ปี"].unique(), reverse=True)
  selected_years = st.sidebar.multiselect("ปี", all_years, default=all_years[:1])
else:
  selected_years = []

# Filter: สังกัด
if "สังกัด" in df_raw.columns:
  all_affiliations = list(df_raw["สังกัด"].unique())
  selected_affiliations = st.sidebar.multiselect(
      "สังกัด", all_affiliations, default=all_affiliations
  )
else:
  selected_affiliations = []

# Filter: หน่วยงาน
if "หน่วยงาน" in df_raw.columns:
  filtered_dept_df = (
      df_raw[df_raw["สังกัด"].isin(selected_affiliations)]
      if selected_affiliations
      else df_raw
  )
  all_depts = list(filtered_dept_df["หน่วยงาน"].unique())
  selected_depts = st.sidebar.multiselect(
      "หน่วยงาน", all_depts, default=all_depts
  )
else:
  selected_depts = []

# Filter: เดือน
month_order = [
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
]
if "เดือน" in df_raw.columns:
  available_months = [m for m in month_order if m in df_raw["เดือน"].unique()]
  if not available_months:
    available_months = list(df_raw["เดือน"].unique())
  selected_months = st.sidebar.multiselect(
      "เดือน", available_months, default=available_months[:5]
  )
else:
  selected_months = []

# คำนวณกรองข้อมูล
df_filtered = df_raw.copy()
if selected_years and "ปี" in df_filtered.columns:
  df_filtered = df_filtered[df_filtered["ปี"].isin(selected_years)]
if selected_affiliations and "สังกัด" in df_filtered.columns:
  df_filtered = df_filtered[df_filtered["สังกัด"].isin(selected_affiliations)]
if selected_depts and "หน่วยงาน" in df_filtered.columns:
  df_filtered = df_filtered[df_filtered["หน่วยงาน"].isin(selected_depts)]
if selected_months and "เดือน" in df_filtered.columns:
  df_filtered = df_filtered[df_filtered["เดือน"].isin(selected_months)]

# ---------------------------------------------------------
# 4. ส่วนหัว Dashboard
# ---------------------------------------------------------
st.title("♻️ Waste Management Dashboard")
st.subheader("Dashboard การจัดการขยะ (กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช)")
st.write(
    "ใช้สำหรับวิเคราะห์ปริมาณขยะ การนำขยะไปใช้ประโยชน์"
    " และปริมาณขยะที่ส่งกำจัด โดยสามารถกรองข้อมูลตามปี สังกัด หน่วยงาน"
    " และเดือนได้"
)

st.divider()

# ---------------------------------------------------------
# 5. สรุปข้อมูล KPI Metrics
# ---------------------------------------------------------
st.header("📊 สรุปข้อมูล")

total_created = (
    float(df_filtered["ขยะที่เกิดขึ้น (กก.)"].sum())
    if "ขยะที่เกิดขึ้น (กก.)" in df_filtered.columns
    else 0.0
)
total_reused = (
    float(df_filtered["นำไปใช้ประโยชน์ (กก.)"].sum())
    if "นำไปใช้ประโยชน์ (กก.)" in df_filtered.columns
    else 0.0
)
total_disposed = (
    float(df_filtered["ขยะที่ส่งกำจัด (กก.)"].sum())
    if "ขยะที่ส่งกำจัด (กก.)" in df_filtered.columns
    else 0.0
)
foam_count = (
    float(df_filtered["โฟมบรรจุอาหาร (ใบ)"].sum())
    if "โฟมบรรจุอาหาร (ใบ)" in df_filtered.columns
    else 0.0
)

reduction_rate = (
    ((total_created - total_disposed) / total_created * 100)
    if total_created > 0
    else 0.0
)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ขยะที่เกิดขึ้น", f"{total_created:,.2f} กก.")
col2.metric("นำไปใช้ประโยชน์", f"{total_reused:,.2f} กก.")
col3.metric("ขยะที่ส่งกำจัด", f"{total_disposed:,.2f} กก.")
col4.metric("เฉลี่ยขยะส่งกำจัดลดลง", f"{reduction_rate:.2f}%")
col5.metric("โฟมบรรจุอาหาร", f"{foam_count:,.0f} ใบ")

st.divider()

# ---------------------------------------------------------
# 6. กราฟแสดงผล (Data Visualization)
# ---------------------------------------------------------
st.header("📈 ปริมาณขยะรายเดือน")
st.caption("แนวโน้มปริมาณขยะรายเดือน")

if not df_filtered.empty and "เดือน" in df_filtered.columns:
  df_monthly = df_filtered.groupby("เดือน", as_index=False)[[
      c
      for c in [
          "ขยะที่เกิดขึ้น (กก.)",
          "นำไปใช้ประโยชน์ (กก.)",
          "ขยะที่ส่งกำจัด (กก.)",
      ]
      if c in df_filtered.columns
  ]].sum()

  df_monthly["เดือน"] = pd.Categorical(
      df_monthly["เดือน"], categories=month_order, ordered=True
  )
  df_monthly = df_monthly.sort_values("เดือน")

  value_cols = [
      c
      for c in [
          "ขยะที่เกิดขึ้น (กก.)",
          "นำไปใช้ประโยชน์ (กก.)",
          "ขยะที่ส่งกำจัด (กก.)",
      ]
      if c in df_monthly.columns
  ]
  df_melted = df_monthly.melt(
      id_vars=["เดือน"],
      value_vars=value_cols,
      var_name="ประเภทขยะ",
      value_name="ปริมาณ (กก.)",
  )

  fig_line = px.line(
      df_melted,
      x="เดือน",
      y="ปริมาณ (กก.)",
      color="ประเภทขยะ",
      markers=True,
      title="แนวโน้มเปรียบเทียบปริมาณขยะตามเดือน",
  )
  fig_line.update_layout(hovermode="x unified")
  st.plotly_chart(fig_line, use_container_width=True)
else:
  st.warning("ไม่มีข้อมูลตามเงื่อนไขที่เลือก")

st.divider()

st.header("📊 การเปรียบเทียบสัดส่วนประเภทขยะ")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
  st.subheader("สัดส่วนการจัดการขยะรวม")
  waste_summary = pd.DataFrame({
      "ประเภท": ["นำไปใช้ประโยชน์", "ส่งกำจัด"],
      "ปริมาณ (กก.)": [total_reused, total_disposed],
  })
  fig_pie = px.pie(
      waste_summary,
      names="ประเภท",
      values="ปริมาณ (กก.)",
      hole=0.4,
      color="ประเภท",
      color_discrete_map={"นำไปใช้ประโยชน์": "#2ca02c", "ส่งกำจัด": "#d62728"},
      title="สัดส่วนการนำไปใช้ประโยชน์ vs ส่งกำจัด",
  )
  st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
  st.subheader("ปริมาณขยะแยกตามสังกัด")
  if "สังกัด" in df_filtered.columns and not df_filtered.empty:
    df_affil = df_filtered.groupby("สังกัด", as_index=False)[
        "ขยะที่เกิดขึ้น (กก.)"
    ].sum()
    fig_bar = px.bar(
        df_affil,
        x="สังกัด",
        y="ขยะที่เกิดขึ้น (กก.)",
        color="สังกัด",
        title="ปริมาณขยะที่เกิดขึ้นแยกตามสังกัด",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.caption(
    "แหล่งข้อมูล:"
    " [data.go.th](https://data.go.th/dataset/gdpublish-69-dnp01-11-01)"
)
