import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="COVID-19 Data Explorer Pro",
    page_icon="🦠",
    layout="wide"
)

# ==================================================
# THEME TOGGLE
# ==================================================
theme = st.sidebar.radio("🎨 Theme Mode", ["Dark", "Light"])
plot_theme = "plotly_dark" if theme == "Dark" else "plotly_white"

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/covid_cleaned_features.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    # Ensure New_Cases exists
    if "New_Cases" not in df.columns:
        if "Confirmed" in df.columns:
            df = df.sort_values(["Country", "Date"])
            df["New_Cases"] = df.groupby("Country")["Confirmed"].diff().fillna(0)
        else:
            df["New_Cases"] = 0

    return df

df_all = load_data()

# ==================================================
# SIDEBAR CONTROLS
# ==================================================
st.sidebar.title("🦠 Controls")

country = st.sidebar.selectbox(
    "Select Country",
    sorted(df_all["Country"].unique())
)

metric_map = {
    "Daily New Cases": "New_Cases",
    "Total Confirmed": "Confirmed",
    "New Confirmed (WHO)": "NewConfirmed",
    "Deaths": "Deaths",
    "Recovered": "Recovered"
}

metric_label = st.sidebar.selectbox(
    "Select Metric",
    list(metric_map.keys())
)

metric_column = metric_map[metric_label]

date_range = st.sidebar.date_input(
    "Date Range",
    [df_all["Date"].min(), df_all["Date"].max()]
)

# ==================================================
# FILTER DATA
# ==================================================
df = df_all[
    (df_all["Country"] == country) &
    (df_all["Date"] >= pd.to_datetime(date_range[0])) &
    (df_all["Date"] <= pd.to_datetime(date_range[1]))
]

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<h1 style="text-align:center;">🦠 COVID-19 Data Explorer Pro</h1>
<p style="text-align:center; font-size:18px;">
Interactive Analytics • Professional Visualization • Real-World Ready
</p>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# KPI METRICS (SAFE)
# ==================================================
c1, c2, c3, c4 = st.columns(4)

total_cases = int(df["Confirmed"].max()) if "Confirmed" in df.columns else 0
max_daily = int(df["New_Cases"].max())
avg_daily = int(df["New_Cases"].mean())
last_date = df["Date"].max().strftime("%Y-%m-%d")

c1.metric("📈 Total Cases", f"{total_cases:,}")
c2.metric("🚨 Max Daily Cases", f"{max_daily:,}")
c3.metric("📉 Avg Daily Cases", f"{avg_daily:,}")
c4.metric("🕒 Last Date", last_date)

# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3 = st.tabs(["📊 Trends", "📦 Distribution", "📁 Upload Data"])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader(f"📊 {metric_label} Trend — {country}")

    fig = px.line(
        df,
        x="Date",
        y=metric_column,
        title=f"{metric_label} Over Time",
        template=plot_theme
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("📦 Distribution of Daily New Cases")

    fig2 = px.histogram(
        df,
        x="New_Cases",
        nbins=40,
        title="Daily New Case Distribution",
        template=plot_theme
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("📁 Upload Your Own Dataset")

    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded:
        user_df = pd.read_csv(uploaded)
        st.success("Dataset loaded successfully!")

        st.dataframe(user_df.head())

        numeric_cols = user_df.select_dtypes(include="number").columns
        if len(numeric_cols) > 0:
            col = st.selectbox("Select numeric column", numeric_cols)
            fig3 = px.histogram(
                user_df,
                x=col,
                title=f"Distribution of {col}",
                template=plot_theme
            )
            st.plotly_chart(fig3, use_container_width=True)

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption("Built with ❤️ using Streamlit • Kaggle COVID-19 Dataset")
