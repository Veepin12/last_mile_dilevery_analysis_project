import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Last-Mile Delivery Performance Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for styling and aesthetics (premium dark mode/modern look)
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
    h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 600;
        color: #f3f4f6;
    }
    .metric-card {
        background-color: #1f2937;
        border-radius: 0.75rem;
        padding: 1.25rem;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .metric-title {
        color: #9ca3af;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #f3f4f6;
        font-size: 1.875rem;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 0.75rem;
        font-weight: 400;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 5px solid #3b82f6;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# Load data helper function (cached)
@st.cache_data
def load_data():
    df = pd.read_csv("last_mile_delivery_cleaned.csv")
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M').dt.hour
    df['is_peak'] = ((df['hour'] >= 8) & (df['hour'] < 10)) | ((df['hour'] >= 17) & (df['hour'] < 20))
    df['is_on_time'] = df['delivery_status'] == 'On-Time'
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.strftime('%B')
    return df

# Initialize data
df = load_data()

# Header
st.title("🚚 Last-Mile Delivery Performance Dashboard")
st.markdown("An interactive operational control board analyzing delays, weather impacts, and on-time performance across 10 Indian cities.")

# Sidebar Filters
st.sidebar.header("🕹️ Control Panel Filters")
st.sidebar.markdown("Filter dashboard metrics in real-time:")

# Weather Filter
all_weather = ['All'] + list(df['weather_condition'].unique())
selected_weather = st.sidebar.selectbox("🌦️ Weather Condition", all_weather, index=0)

# Time of Day Filter
time_filter_options = ["All", "Peak Hours (8-10 AM, 5-8 PM)", "Off-Peak Hours"]
selected_time = st.sidebar.selectbox("⏰ Time of Day", time_filter_options, index=0)

# Apply filters to dataframe
filtered_df = df.copy()

if selected_weather != 'All':
    filtered_df = filtered_df[filtered_df['weather_condition'] == selected_weather]

if selected_time == "Peak Hours (8-10 AM, 5-8 PM)":
    filtered_df = filtered_df[filtered_df['is_peak'] == True]
elif selected_time == "Off-Peak Hours":
    filtered_df = filtered_df[filtered_df['is_peak'] == False]

# Top KPI Metrics Cards Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = len(filtered_df)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📦 Total Orders Analyzed</div>
        <div class="metric-value">{total_orders:,}</div>
        <div class="metric-sub" style="color: #9ca3af;">Filtered subset size</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_on_time = filtered_df['is_on_time'].mean() * 100 if total_orders > 0 else 0
    color = "#10b981" if avg_on_time >= 50 else "#f59e0b" if avg_on_time >= 35 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🎯 Average On-Time Rate</div>
        <div class="metric-value" style="color: {color};">{avg_on_time:.2f}%</div>
        <div class="metric-sub" style="color: #9ca3af;">Target SLA: 95%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    median_delay = filtered_df['delay_mins'].median() if total_orders > 0 else 0
    color_del = "#10b981" if median_delay <= 10 else "#f59e0b" if median_delay <= 20 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">⏱️ Median Delay</div>
        <div class="metric-value" style="color: {color_del};">{median_delay:.1f} mins</div>
        <div class="metric-sub" style="color: #9ca3af;">Median time over promised</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    worst_city = "N/A"
    worst_rate = 0.0
    if total_orders > 0:
        city_stats = filtered_df.groupby('city')['is_on_time'].mean()
        if len(city_stats) > 0:
            worst_city = city_stats.idxmin()
            worst_rate = city_stats.min() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">⚠️ Lowest On-Time City</div>
        <div class="metric-value" style="color: #ef4444;">{worst_city}</div>
        <div class="metric-sub" style="color: #ef4444;">On-Time: {worst_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Dashboard Panels
panel_col1, panel_col2 = st.columns(2)

with panel_col1:
    st.subheader("📊 Panel 1: City-Wise On-Time Rate")
    if total_orders > 0:
        city_on_time_df = filtered_df.groupby('city')['is_on_time'].mean().reset_index()
        city_on_time_df['on_time_rate'] = city_on_time_df['is_on_time'] * 100
        city_on_time_df = city_on_time_df.sort_values(by='on_time_rate', ascending=True)

        chart1 = alt.Chart(city_on_time_df).mark_bar().encode(
            x=alt.X('on_time_rate:Q', title='On-Time Rate (%)', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('city:N', sort='-x', title='City'),
            color=alt.Color('on_time_rate:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
            tooltip=['city', alt.Tooltip('on_time_rate:Q', format='.2f')]
        ).properties(height=350)
        
        st.altair_chart(chart1, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

with panel_col2:
    st.subheader("📈 Panel 2: Monthly Delay Trend")
    if total_orders > 0:
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        monthly_df = filtered_df.groupby(['month', 'month_name'])['delay_mins'].median().reset_index()
        
        chart2 = alt.Chart(monthly_df).mark_line(point=True, strokeWidth=3, color='#3b82f6').encode(
            x=alt.X('month_name:N', sort=month_order, title='Month'),
            y=alt.Y('delay_mins:Q', title='Median Delay (Minutes)'),
            tooltip=['month_name', alt.Tooltip('delay_mins:Q', format='.1f')]
        ).properties(height=350)
        
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

# Third Panel (Vehicle Type Comparison) and Key Metrics
panel_col3, panel_col4 = st.columns(2)

with panel_col3:
    st.subheader("🛵 Panel 3: Vehicle Type Comparison")
    if total_orders > 0:
        vehicle_df = filtered_df.groupby('vehicle_type')[['delay_mins', 'is_on_time']].agg(
            median_delay=('delay_mins', 'median'),
            on_time_rate=('is_on_time', 'mean')
        ).reset_index()
        vehicle_df['on_time_rate'] = vehicle_df['on_time_rate'] * 100

        # Bar chart for median delay
        chart3 = alt.Chart(vehicle_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('vehicle_type:N', title='Vehicle Type'),
            y=alt.Y('median_delay:Q', title='Median Delay (Minutes)'),
            color=alt.value('#10b981'),
            tooltip=['vehicle_type', alt.Tooltip('median_delay:Q', format='.1f')]
        ).properties(height=300)
        
        st.altair_chart(chart3, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

with panel_col4:
    st.subheader("🏷️ Operational Diagnostics")
    if total_orders > 0:
        # Display weather summary table
        weather_summary = df.groupby('weather_condition')['delay_mins'].agg(
            Median_Delay='median',
            On_Time_Rate=lambda x: f"{(x == 'On-Time').mean() * 100:.1f}%"
        ).rename(columns={'On_Time_Rate': 'On-Time Rate'})
        
        # Display peak hour summary
        peak_summary = df.groupby('is_peak')['delay_mins'].agg(
            Median_Delay='median',
            On_Time_Rate=lambda x: f"{(df.loc[x.index, 'delivery_status'] == 'On-Time').mean() * 100:.1f}%"
        )
        peak_summary.index = ['Off-Peak Hours', 'Peak Hours (8-10 AM, 5-8 PM)']
        
        st.markdown("**Weather Conditions Performance (Whole Dataset)**")
        st.dataframe(weather_summary, use_container_width=True)
        
        st.markdown("**Traffic Peak Hours Performance (Whole Dataset)**")
        st.dataframe(peak_summary, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

# Section 4: Operational Recommendations
st.markdown("""
<div class="recommendation-box">
    <h3>💡 Single Biggest Operational Fix: Transition to Dynamic SLAs</h3>
    <p>
        The data reveals that the overall on-time rate is extremely low, averaging only <b>35.0%</b>. 
        However, the root cause is not individual rider experience (p-value = 0.567) or vehicle efficiency. 
        Instead, it is driven by <b>rigid, static SLA targets (30-60 minutes)</b> that fail to account for highly predictable temporal and environmental disruptions:
    </p>
    <ul>
        <li><b>Peak Hours</b>: Peak traffic hours (8-10 AM, 5-8 PM) increase median delays by <b>+13.9 minutes</b>, dropping on-time rates to <b>18.9%</b>.</li>
        <li><b>Adverse Weather</b>: Rain increases median delays by <b>+23.3 minutes</b> (dropping on-time rates to <b>10.7%</b>). Fog increases median delays by <b>+31.8 minutes</b> (dropping on-time rates to <b>4.2%</b>).</li>
        <li><b>Compound Effects</b>: During peak hours in the rain, the on-time rate drops to a critical <b>1.56%</b>. During peak hours in the fog, the on-time rate is <b>0.00%</b>.</li>
    </ul>
    <p>
        <b>Actionable Fix:</b> Implement <b>Dynamic SLA Buffers</b> in the customer ordering system. 
        Instead of promising 30 or 60 minutes, the promised delivery times should dynamically adjust:
        <br>
        1. <b>Peak Traffic Buffer</b>: Add <b>+15 minutes</b> during 8-10 AM and 5-8 PM.
        <br>
        2. <b>Weather Buffer</b>: Add <b>+25 minutes</b> when rain is detected, and <b>+35 minutes</b> when fog is present.
    </p>
    <p>
        This simple software-driven fix will immediately match customer expectations with physical traffic and weather realities, 
        improve the brand's official on-time SLA metrics, and significantly protect delivery rider safety by removing the pressure 
        to execute impossible deliveries under hazardous conditions.
    </p>
</div>
""", unsafe_allow_html=True)
