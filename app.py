from pathlib import Path
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
SEASONS = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SEASON_COLORS = {
    "Winter": "#6c9ebc",
    "Summer": "#e4ad61",
    "Monsoon": "#3b8c79",
    "Post-Monsoon": "#86a865",
}
CLIMATE_FIELDS = {
    "Temp": "Temperature (°C)",
    "preci": "Precipitation (source units)",
    "LAI": "Leaf area index",
}
DATA_PATHS = [
    BASE_DIR / "Data" / "processed" / "Maharashtra_Feature_Engineered.csv",
    BASE_DIR / "Data" / "processed" / "Maharashtra_Seasonal_Disease_Cleaned.csv",
]
# Public creator links shown in the site footer.
LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/huzaifa-baig-509803388/"
CONTACT_EMAIL = "anotherhuzaifa@gmail.com"

st.set_page_config(
    page_title="Analysis of Diseases in Maharashtra",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto",
)


def fmt_num(value):
    return f"{value:,.0f}"


def normalize_data(frame):
    df = frame.copy()
    df.columns = [str(c).strip() for c in df.columns]
    lower_lookup = {c.lower(): c for c in df.columns}
    aliases = {
        "Date": ["date"],
        "District": ["district"],
        "Disease": ["disease"],
        "Cases": ["cases"],
        "Deaths": ["deaths"],
        "state_ut": ["state_ut", "state", "state/ut"],
        "Temp": ["temp", "temperature"],
        "preci": ["preci", "precipitation", "rainfall"],
        "LAI": ["lai"],
        "Year": ["year"],
        "Month": ["month", "mon"],
        "Day": ["day"],
        "Latitude": ["latitude", "lat"],
        "Longitude": ["longitude", "lon", "lng"],
    }
    for canonical, names in aliases.items():
        if canonical not in df:
            for name in names:
                if name in lower_lookup:
                    df[canonical] = df[lower_lookup[name]]
                    break
    if "Date" not in df and all(c in df for c in ["Year", "Month", "Day"]):
        df["Date"] = pd.to_datetime(
            {"year": df["Year"], "month": df["Month"], "day": df["Day"]}, errors="coerce"
        )
    elif "Date" in df:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    required = ["Date", "Disease", "Cases"]
    missing = [col for col in required if col not in df]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    if "District" not in df:
        df["District"] = "Not recorded"
    if "state_ut" in df:
        is_maharashtra = df["state_ut"].astype(str).str.strip().str.casefold().eq("maharashtra")
        if is_maharashtra.any():
            df = df.loc[is_maharashtra].copy()

    df["Cases"] = pd.to_numeric(df["Cases"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    for col in ["Deaths", "Temp", "preci", "LAI", "Latitude", "Longitude"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Disease"] = df["Disease"].astype(str).str.strip()
    df["District"] = df["District"].astype(str).str.strip()
    df = df.dropna(subset=["Date", "Cases"])
    df = df[df["Cases"] >= 0].copy()
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month label"] = df["Date"].dt.strftime("%b")
    df["Season"] = df["Month"].map(
        lambda month: "Summer" if month in (3, 4, 5)
        else "Monsoon" if month in (6, 7, 8, 9)
        else "Post-Monsoon" if month in (10, 11)
        else "Winter"
    )
    if "Temp" in df:
        # The notebook identifies Temp as Kelvin and also provides a Celsius conversion.
        df["Temperature_C"] = df["Temp"] - 273.15
    return df


def style_chart(fig, height=360):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        font=dict(family="DM Sans, sans-serif", color="#29483f", size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        legend=dict(font=dict(color="#38574d", size=12)),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#cbd8d0",
        tickfont=dict(color="#526a60", size=12),
        title_font=dict(color="#3e5c50", size=13),
        showticklabels=True,
    )
    fig.update_yaxes(
        gridcolor="#e4ebe6",
        zerolinecolor="#d2ded6",
        tickfont=dict(color="#526a60", size=12),
        title_font=dict(color="#3e5c50", size=13),
        showticklabels=True,
    )
    return fig


def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file), uploaded_file.name
    for path in DATA_PATHS:
        if path.exists():
            return pd.read_csv(path), path.name
    return None, None


def page_header(eyebrow, title, description):
    st.markdown(f"<div class='eyebrow'>{eyebrow}</div>", unsafe_allow_html=True)
    st.title(title)
    st.markdown(f"<p class='page-description'>{description}</p>", unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --forest:#123f38; --teal:#2f806f; --mint:#e7f1ec; --ink:#1c3933; --muted:#71867e; --line:#e4ebe6; }
.stApp { background:#f5f7f5; color:var(--ink); font-family:'DM Sans',sans-serif; }
.block-container { max-width:1440px; padding:1.5rem 2.5rem 3rem; }
[data-testid="stSidebar"] { background:#103c36; border-right:1px solid #214d45; }
[data-testid="stSidebar"] * { color:#f2f7f4 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { background:transparent; border-radius:10px; padding:3px 7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#24554b; }
[data-testid="stSidebar"] hr { border-color:#315d53; }
h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.035em; color:#183a33; }
h1 { font-size:2.3rem !important; margin:0 0 .2rem; }
.brand-lockup { padding:8px 4px 20px; }
.brand-mark { width:43px;height:43px;border-radius:14px;background:#d6edce;color:#173f37;display:inline-flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:12px; }
.brand-name { font-family:'Manrope',sans-serif;font-weight:800;font-size:1.12rem;line-height:1.2;color:#fff; }
.brand-sub { font-size:.8rem;color:#b8d0c8;margin-top:5px; }
.eyebrow { color:#5d8a79; text-transform:uppercase; letter-spacing:.14em; font-size:.73rem; font-weight:700; margin-bottom:7px; }
.page-description { color:#687f75;max-width:870px;font-size:1rem;margin:.15rem 0 1.4rem; }
.hero { background:linear-gradient(112deg,#133f37 0%,#286b5b 70%,#4e9273 100%); border-radius:22px; padding:29px 34px; color:#fff; margin-bottom:21px; position:relative; overflow:hidden; }
.hero:after { content:' ';position:absolute;width:250px;height:250px;border:1px solid #ffffff22;border-radius:50%;right:-48px;top:-110px;box-shadow:0 0 0 35px #ffffff09,0 0 0 72px #ffffff07; }
.hero .eyebrow { color:#c6e6ba; }
.hero h1 { color:#fff;font-size:2.15rem !important;margin:5px 0 8px; }
.hero p { color:#e0eee7;max-width:820px;margin:0;font-size:1rem; }
.hero-badge { display:inline-block;background:#ffffff18;border:1px solid #ffffff35;color:#f4fbf5;border-radius:30px;padding:7px 12px;font-size:.78rem;margin-top:18px; }
.section-label { color:#65907e;text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:700;margin:1rem 0 .3rem; }
.soft-note { background:#e9f1ed;border:1px solid #d9e7de;border-radius:12px;padding:13px 16px;color:#365a4d;font-size:.9rem; }
.stMetric, [data-testid="stMetric"] { background:#fff;border:1px solid var(--line);padding:15px 18px;border-radius:15px;box-shadow:0 4px 18px #173f3710; }
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] *, [data-testid="stMetric"] label, [data-testid="stMetric"] label * { color:#526c60 !important; opacity:1 !important; }
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *, [data-testid="stMetric"] [data-testid="stMetricValue"] { color:#183f36 !important; font-family:'Manrope',sans-serif; font-size:1.85rem !important; line-height:1.2 !important; }
div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] * { color:#527365 !important; }
[data-testid="stPlotlyChart"] { background:white;border:1px solid #e5ece7;border-radius:16px;padding:9px 10px;box-shadow:0 4px 15px #193e3508; }
div[data-testid="stSelectbox"],div[data-testid="stMultiSelect"],div[data-testid="stSlider"] { margin-bottom:.5rem; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:9px 9px 0 0; }
.footer { border-top:1px solid #dce7e0;margin-top:2.4rem;padding:1.25rem 0 .5rem;color:#71867d;font-size:.8rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap; }
.footer-credit { display:flex;flex-direction:column;line-height:1.05; }
.footer-credit-label { color:#6f837a;font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700; }
.footer-signature { color:#17483d;font-family:'Caveat','Segoe Script',cursive;font-size:2.15rem;font-weight:600;line-height:1.15;margin-top:3px; }
.footer-links { display:flex;gap:1.1rem;align-items:center; }
.footer-links a { color:#277563 !important;font-weight:600;text-decoration:none; }
.footer-links a:hover { color:#17483d !important;text-decoration:underline; }
.footer-note { color:#87968f;text-align:right; }
@media (max-width:900px) {
    .block-container { padding:1rem 1.25rem 2rem; }
    .hero { padding:24px; }
    .hero h1 { font-size:1.8rem !important; }
}
@media (max-width:680px) {
    .block-container { padding:.8rem .8rem 1.5rem; }
    h1 { font-size:1.75rem !important; }
    h2 { font-size:1.35rem !important; }
    h3 { font-size:1.1rem !important; }
    .hero { padding:20px 18px; border-radius:16px; margin-bottom:16px; }
    .hero h1 { font-size:1.55rem !important; }
    .hero p { font-size:.92rem; }
    .hero-badge { font-size:.72rem; line-height:1.5; border-radius:12px; }
    .page-description { font-size:.92rem; margin-bottom:1rem; }
    [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:.6rem; }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex:1 1 100% !important;
        min-width:100% !important;
        width:100% !important;
    }
    [data-testid="stMetric"] { padding:12px 14px; }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *,
    [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size:1.55rem !important; }
    [data-testid="stPlotlyChart"] { padding:5px; border-radius:12px; }
    .stTabs [data-baseweb="tab-list"] { overflow-x:auto; flex-wrap:nowrap; gap:4px; }
    .stTabs [data-baseweb="tab"] { white-space:nowrap; padding:8px 10px; }
    .footer { align-items:flex-start; flex-direction:column; gap:.6rem; }
    .footer-note { text-align:left; }
    .footer-signature { font-size:1.9rem; }
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="brand-lockup"><div class="brand-mark">✦</div>
    <div class="brand-name">Maharashtra<br>Health Watch</div>
    <div class="brand-sub">Seasonal disease awareness</div></div>
    """, unsafe_allow_html=True)
    st.divider()
    section = st.radio(
        "Navigate",
        ["Home", "Explore Trends", "Insights Summary", "Climate Insights", "Awareness & Prevention"],
        label_visibility="collapsed",
    )
    st.divider()
    uploaded = st.file_uploader("Use another dataset", type=["csv"], help="The project CSV loads automatically. Upload a replacement if needed.")

try:
    raw, data_source = load_data(uploaded)
    if raw is None:
        st.markdown("<div class='hero'><div class='eyebrow'>Maharashtra • Public health awareness</div><h1>Understand the seasons.<br>Stay informed.</h1><p>Explore historical disease patterns, district differences and recorded climate measures in one clear dashboard.</p></div>", unsafe_allow_html=True)
        st.info("Place the processed CSV in Data/processed or upload it from the sidebar to begin.")
        st.markdown("Expected files: `Maharashtra_Feature_Engineered.csv` or `Maharashtra_Seasonal_Disease_Cleaned.csv`. Required columns: `Date` (or Year, Month, Day), `Disease`, and `Cases`.")
        st.stop()
    df = normalize_data(raw)
except Exception as exc:
    st.error(f"Could not read this dataset: {exc}")
    st.markdown("Required fields are `Date` (or Year, Month, Day), `Disease`, and `Cases`.")
    st.stop()

if df.empty:
    st.warning("No valid dated case records were found in this dataset.")
    st.stop()

if section == "Home":
    page_header("MAHARASHTRA · HISTORICAL SURVEILLANCE", "Analysis of Diseases in Maharashtra", "A clear, community-friendly view of historical reports across Maharashtra. Explore what was recorded, when patterns changed, and where reports came from.")
    st.markdown(f"<div class='hero'><div class='eyebrow'>Historical data overview</div><h1>See the pattern.<br>Make sense of the season.</h1><p>Explore reported cases across seasons and districts, then find practical ways to stay informed. Historical patterns describe the dataset; they do not predict what will happen next.</p><span class='hero-badge'>Data coverage: {df.Date.min():%Y}–{df.Date.max():%Y} &nbsp;•&nbsp; Source: project surveillance dataset</span></div>", unsafe_allow_html=True)

    records = len(df)
    st.markdown("<div class='section-label'>The dataset at a glance</div>", unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Historical period", f"{df.Date.min():%Y}–{df.Date.max():%Y}")
    k2.metric("Districts represented", fmt_num(df.District.nunique()))
    k3.metric("Disease categories", fmt_num(df.Disease.nunique()))
    k4.metric("Reported cases", fmt_num(df.Cases.sum()))
    st.caption(f"{fmt_num(records)} dated records are available in the selected dataset. Counts are not population-adjusted rates.")

    left,right=st.columns([1.2,1])
    with left:
        st.subheader("When reports were recorded")
        yearly=df.groupby("Year",as_index=False).Cases.sum()
        fig=px.area(yearly,x="Year",y="Cases",markers=True,color_discrete_sequence=["#3e8a76"])
        fig.update_traces(line=dict(width=3),fillcolor="rgba(62,138,118,0.15)",hovertemplate="%{x}: %{y:,.0f} reported cases<extra></extra>")
        st.plotly_chart(style_chart(fig,330),use_container_width=True)
    with right:
        st.subheader("Reports by season")
        seasonal=df.groupby("Season",as_index=False).Cases.sum()
        seasonal["Season"]=pd.Categorical(seasonal.Season,SEASONS,ordered=True)
        seasonal=seasonal.sort_values("Season")
        fig=px.bar(seasonal,x="Season",y="Cases",color="Season",color_discrete_map=SEASON_COLORS)
        fig.update_traces(hovertemplate="%{x}: %{y:,.0f} reported cases<extra></extra>")
        st.plotly_chart(style_chart(fig,330),use_container_width=True)
        peak_season=seasonal.sort_values("Cases",ascending=False).iloc[0]
        st.markdown(f"<div class='soft-note'>In the selected dataset, <b>{peak_season.Season}</b> has the largest seasonal total ({fmt_num(peak_season.Cases)} reported cases). This describes available records and may also reflect differences in reporting coverage.</div>",unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Explore the Maharashtra picture</div>",unsafe_allow_html=True)
    map_col, disease_col = st.columns([1.15,1])
    with map_col:
        st.subheader("Districts represented in the dataset")
        if all(c in df for c in ["Latitude","Longitude"]) and df[["Latitude","Longitude"]].notna().any(axis=None):
            loc=df.dropna(subset=["Latitude","Longitude"]).groupby("District",as_index=False).agg(Latitude=("Latitude","mean"),Longitude=("Longitude","mean"),Cases=("Cases","sum"),Records=("Cases","size"))
            fig=px.scatter_geo(loc,lat="Latitude",lon="Longitude",size="Records",color="Cases",hover_name="District",hover_data={"Cases":":,.0f","Records":True,"Latitude":False,"Longitude":False},color_continuous_scale=["#c8e0d2","#4f9a7e","#175247"],size_max=18)
            fig.update_geos(projection_type="mercator",center={"lat":19.5,"lon":76.2},lataxis_range=[14.5,22.5],lonaxis_range=[72.2,81.5],showland=True,landcolor="#edf2ed",showocean=True,oceancolor="#edf5f5",showcoastlines=False,showframe=False)
            st.plotly_chart(style_chart(fig,390),use_container_width=True)
            st.caption("Dots use the average coordinates recorded for each district. Color shows case totals; it is not a risk rating.")
        else:
            st.info("District coordinates are not available in this dataset, so the map cannot be shown.")
    with disease_col:
        st.subheader("Most reported categories")
        top=df.groupby("Disease",as_index=False).Cases.sum().sort_values("Cases").tail(8)
        fig=px.bar(top,x="Cases",y="Disease",orientation="h",color_discrete_sequence=["#2f806f"])
        fig.update_traces(hovertemplate="%{y}: %{x:,.0f} reported cases<extra></extra>")
        st.plotly_chart(style_chart(fig,390),use_container_width=True)
        st.caption("Categories are kept as recorded in the cleaned dataset.")

    with st.expander("Notebook EDA chart gallery"):
        st.caption("Original charts saved by the attached EDA and statistical-analysis notebooks. These show the notebooks’ full dataset and are not affected by dashboard filters.")
        chart_files=sorted((BASE_DIR/"assets"/"notebook-eda").glob("*.png"))
        if chart_files:
            chart_names=[p.name for p in chart_files]
            selected_chart=st.selectbox("Choose a notebook chart",chart_names,format_func=lambda n:n.replace("_"," ").removesuffix(".png"))
            st.image(str(next(p for p in chart_files if p.name==selected_chart)),use_container_width=True)

elif section == "Explore Trends":
    page_header("EXPLORE THE HISTORY", "Explore disease trends", "Choose a disease, season, year range or district to see how historical reports vary across time and place.")
    with st.sidebar:
        st.markdown("### Explore filters")
        disease_options=sorted(df.Disease.unique().tolist())
        disease=st.selectbox("Disease",["All categories"]+disease_options)
        year_min,year_max=int(df.Year.min()),int(df.Year.max())
        year_range=st.slider("Year range",year_min,year_max,(year_min,year_max)) if year_min<year_max else (year_min,year_max)
        season_options=st.multiselect("Season",SEASONS,default=SEASONS)
        district_options=sorted(df.District.unique().tolist())
        districts=st.multiselect("District",district_options,default=district_options)
    view=df[df.Year.between(*year_range)&df.Season.isin(season_options)&df.District.isin(districts)].copy()
    if disease!="All categories": view=view[view.Disease.eq(disease)]
    if view.empty:
        st.warning("No records match those filters. Try widening the year range or selecting more seasons or districts.")
        st.stop()
    m1,m2,m3=st.columns(3)
    m1.metric("Reported cases",fmt_num(view.Cases.sum()))
    m2.metric("Dated records",fmt_num(len(view)))
    m3.metric("Districts in view",fmt_num(view.District.nunique()))
    st.caption(f"Showing {view.Date.min():%d %b %Y} to {view.Date.max():%d %b %Y}. Counts reflect the selected records, not population-adjusted rates.")

    tab1,tab2,tab3=st.tabs(["Over time","Seasonal pattern","By district"])
    with tab1:
        a,b=st.columns([1.2,1])
        with a:
            st.subheader("Year-by-year reports")
            annual=view.groupby(["Year","Disease"],as_index=False).Cases.sum()
            fig=px.line(annual,x="Year",y="Cases",color="Disease",markers=True,color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(style_chart(fig,375),use_container_width=True)
        with b:
            st.subheader("Monthly pattern")
            monthly=view.groupby(["Month","Month label"],as_index=False).Cases.sum().sort_values("Month")
            fig=px.bar(monthly,x="Month label",y="Cases",color_discrete_sequence=["#4b8b78"])
            fig.update_xaxes(categoryorder="array",categoryarray=MONTHS)
            st.plotly_chart(style_chart(fig,375),use_container_width=True)
        st.caption("Monthly bars total the reports recorded for each calendar month across the selected years.")
    with tab2:
        a,b=st.columns([1,1.1])
        with a:
            st.subheader("Season totals")
            seasonal=view.groupby(["Season","Disease"],as_index=False).Cases.sum()
            seasonal["Season"]=pd.Categorical(seasonal.Season,SEASONS,ordered=True)
            seasonal=seasonal.sort_values("Season")
            fig=px.bar(seasonal,x="Season",y="Cases",color="Disease",barmode="stack",color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(style_chart(fig,385),use_container_width=True)
        with b:
            st.subheader("Disease reports by month")
            heat=view.pivot_table(index="Disease",columns="Month label",values="Cases",aggfunc="sum",fill_value=0)
            heat=heat.reindex(columns=MONTHS,fill_value=0)
            fig=px.imshow(heat,aspect="auto",color_continuous_scale=["#f4f7f4","#d5e8dd","#4e967c"],labels=dict(x="Month",y="Disease",color="Cases"))
            fig.update_layout(height=max(330,28*len(heat)+100),margin=dict(l=8,r=8,t=20,b=8))
            fig.update_coloraxes(colorbar_tickfont=dict(color="#526a60"),colorbar_title_font=dict(color="#3e5c50"))
            st.plotly_chart(style_chart(fig,max(370,28*len(heat)+100)),use_container_width=True)
        st.caption("Seasons follow the notebook definition: Summer (Mar–May), Monsoon (Jun–Sep), Post-Monsoon (Oct–Nov), Winter (Dec–Feb).")
    with tab3:
        st.subheader("District totals in the selected view")
        district_totals=view.groupby("District",as_index=False).Cases.sum().sort_values("Cases",ascending=False)
        district_top=district_totals.head(15).sort_values("Cases")
        fig=px.bar(district_top,x="Cases",y="District",orientation="h",color_discrete_sequence=["#ca925b"])
        st.plotly_chart(style_chart(fig,440),use_container_width=True)
        st.caption("These are totals in the available records. They do not account for district population or reporting completeness.")
        with st.expander("View district totals"):
            st.dataframe(district_totals,use_container_width=True,hide_index=True)
    with st.expander("Download or inspect selected records"):
        keep=[c for c in ["Date","Year","Season","District","Disease","Cases","Deaths"] if c in view]
        st.dataframe(view[keep].sort_values("Date",ascending=False),use_container_width=True,hide_index=True)
        st.download_button("Download filtered records",view[keep].to_csv(index=False).encode("utf-8"),"maharashtra_filtered_records.csv","text/csv")

elif section == "Insights Summary":
    page_header("KEY FINDINGS FROM THE DATA", "Insights summary", "A structured summary of which diseases and seasons account for the most reports, how districts differ, and which climate measurements appear alongside those reports.")
    st.markdown(f"<div class='soft-note'>This summary covers <b>{df.Date.min():%Y}–{df.Date.max():%Y}</b> in the dataset. All figures are totals or averages of available records; they are not population-adjusted rates, current surveillance, or forecasts.</div>",unsafe_allow_html=True)

    season_totals=df.groupby("Season").Cases.sum().reindex(SEASONS,fill_value=0)
    disease_totals=df.groupby("Disease").Cases.sum().sort_values(ascending=False)
    district_totals=df.groupby("District").Cases.sum().sort_values(ascending=False)
    disease_season=df.pivot_table(index="Disease",columns="Season",values="Cases",aggfunc="sum",fill_value=0).reindex(columns=SEASONS,fill_value=0)
    disease_peak=disease_season.idxmax(axis=1)
    disease_peak_cases=disease_season.max(axis=1)
    district_disease=df.pivot_table(index="District",columns="Disease",values="Cases",aggfunc="sum",fill_value=0)
    district_leader=district_disease.idxmax(axis=1)
    district_leader_cases=district_disease.max(axis=1)

    top_season=season_totals.idxmax()
    top_disease=disease_totals.index[0]
    top_district=district_totals.index[0]
    top_pair=disease_season.stack().sort_values(ascending=False).index[0]
    top_pair_cases=disease_season.loc[top_pair[0],top_pair[1]]
    a,b,c,d=st.columns(4)
    a.metric("Largest seasonal total",top_season,fmt_num(season_totals[top_season])+" reports")
    b.metric("Most reported disease",top_disease,fmt_num(disease_totals.iloc[0])+" cases")
    c.metric("Largest district total",top_district,fmt_num(district_totals.iloc[0])+" cases")
    d.metric("Largest disease-season pair",top_pair[0],f"{top_pair[1]} · {fmt_num(top_pair_cases)}")

    st.subheader("What stands out in this dataset")
    st.markdown(
        f"- **Season:** {top_season} has the highest total, with **{fmt_num(season_totals[top_season])}** reported cases.  \n"
        f"- **Disease:** {top_disease} has the largest overall total, with **{fmt_num(disease_totals.iloc[0])}** cases.  \n"
        f"- **District:** {top_district} has the largest total in the available reports, with **{fmt_num(district_totals.iloc[0])}** cases.  \n"
        f"- **Peak combination:** {top_pair[0]} has its largest seasonal total in **{top_pair[1]}** ({fmt_num(top_pair_cases)} cases)."
    )

    st.subheader("Which season is the peak for each disease?")
    left,right=st.columns([1.2,1])
    with left:
        heat_order=disease_season.sum(axis=1).sort_values(ascending=False).index
        fig=px.imshow(disease_season.loc[heat_order],aspect="auto",color_continuous_scale=["#f2f6f3","#bedcc9","#3f9279"],labels=dict(x="Season",y="Disease",color="Reported cases"),text_auto=".0f")
        fig.update_layout(height=max(350,27*len(disease_season)+110),margin=dict(l=8,r=8,t=20,b=8))
        st.plotly_chart(style_chart(fig,max(390,27*len(disease_season)+110)),use_container_width=True)
    with right:
        disease_profile=df.groupby("Disease",as_index=False).agg(Reported_Cases=("Cases","sum"),Records=("Cases","size"))
        disease_profile["Peak_Season"]=disease_profile.Disease.map(disease_peak)
        disease_profile["Cases_in_Peak_Season"]=disease_profile.Disease.map(disease_peak_cases)
        disease_profile["Peak_Season_Share_%"]=(disease_profile.Cases_in_Peak_Season/disease_profile.Reported_Cases*100).round(1)
        disease_profile=disease_profile.sort_values("Reported_Cases",ascending=False)
        st.dataframe(disease_profile.rename(columns={"Reported_Cases":"Total cases","Records":"Records","Peak_Season":"Peak season","Cases_in_Peak_Season":"Cases in peak season","Peak_Season_Share_%":"Peak-season share (%)"}),use_container_width=True,hide_index=True,height=390)
    st.caption("Peak season means the season with the largest sum of recorded cases for that disease in this dataset. It does not indicate an individual or current risk level.")

    st.subheader("District-by-district summary")
    left,right=st.columns([1,1.15])
    with left:
        district_view=df.groupby("District",as_index=False).agg(Reported_Cases=("Cases","sum"),Records=("Cases","size"))
        district_view["Most_Reported_Disease"]=district_view.District.map(district_leader)
        district_view["Disease_Cases_in_District"]=district_view.District.map(district_leader_cases)
        district_view=district_view.sort_values("Reported_Cases",ascending=False)
        st.dataframe(district_view.rename(columns={"District":"District","Reported_Cases":"Total cases","Records":"Records","Most_Reported_Disease":"Largest category","Disease_Cases_in_District":"Category cases"}),use_container_width=True,hide_index=True,height=430)
    with right:
        top_districts=district_view.head(15).sort_values("Reported_Cases")
        fig=px.bar(top_districts,x="Reported_Cases",y="District",orientation="h",color_discrete_sequence=["#4b8b78"],hover_data={"Records":True,"Most_Reported_Disease":True})
        fig.update_layout(xaxis_title="Reported cases",yaxis_title="District")
        st.plotly_chart(style_chart(fig,430),use_container_width=True)
        st.caption("The leading category in a district reflects its largest total among recorded categories, not its population-adjusted burden.")

    st.subheader("Weather measures recorded alongside each disease")
    climate_cols=[c for c in ["Temp","preci","LAI"] if c in df and df[c].notna().any()]
    if climate_cols:
        climate_df=df.copy()
        if "Temp" in climate_df:
            climate_df["Temperature_C"]=climate_df["Temp"]-273.15
        agg_spec={"Total_cases":("Cases","sum"),"Records":("Cases","size")}
        if "Temp" in climate_cols:
            agg_spec["Average_temperature_C"]=("Temperature_C","mean")
            agg_spec["Temperature_records"]=("Temperature_C","count")
        if "preci" in climate_cols:
            agg_spec["Average_precipitation_source_units"]=("preci","mean")
            agg_spec["Precipitation_records"]=("preci","count")
        if "LAI" in climate_cols:
            agg_spec["Average_LAI"]=("LAI","mean")
            agg_spec["LAI_records"]=("LAI","count")
        weather_summary=climate_df.groupby("Disease",as_index=False).agg(**agg_spec).sort_values("Total_cases",ascending=False)
        for col in ["Average_temperature_C","Average_precipitation_source_units","Average_LAI"]:
            if col in weather_summary:
                weather_summary[col]=weather_summary[col].round(2)
        weather_labels={
            "Disease":"Disease",
            "Total_cases":"Reported cases",
            "Records":"Records",
            "Average_temperature_C":"Avg. temperature (°C)",
            "Temperature_records":"Temp. readings",
            "Average_precipitation_source_units":"Avg. precipitation (source units)",
            "Precipitation_records":"Precip. readings",
            "Average_LAI":"Avg. leaf area index",
            "LAI_records":"LAI readings",
        }
        st.dataframe(weather_summary.rename(columns=weather_labels),use_container_width=True,hide_index=True)
        st.caption("Climate averages use records where each measurement is present. Temperature is converted from Kelvin to °C; the precipitation unit is not documented in the source files. LAI means leaf area index. Averages combine dates and districts and are descriptive only; they do not show that weather caused disease reports.")
    else:
        st.info("The loaded dataset has no usable Temp, preci, or LAI measurements.")

    with st.expander("How this summary is calculated"):
        st.markdown("Season totals sum the case counts assigned to each calendar season. Disease peaks use each disease’s highest seasonal case total. District leaders use the disease with the most reported cases in that district. Weather averages are means across available rows for each disease. Reporting coverage, population size, and other factors are not controlled for.")

elif section == "Climate Insights":
    page_header("CLIMATE & HISTORICAL REPORTS", "Climate and disease insights", "Compare recorded climate measurements with reported cases over time. The charts describe co-occurrence; they do not show that one caused the other.")
    with st.sidebar:
        st.markdown("### Climate filters")
        climate_years=st.slider("Year range",int(df.Year.min()),int(df.Year.max()),(int(df.Year.min()),int(df.Year.max()))) if df.Year.min()<df.Year.max() else (int(df.Year.min()),int(df.Year.max()))
        climate_disease=st.selectbox("Disease category",["All categories"]+sorted(df.Disease.unique().tolist()))
        climate_districts=st.multiselect("District",sorted(df.District.unique().tolist()),default=sorted(df.District.unique().tolist()))
    cview=df[df.Year.between(*climate_years)&df.District.isin(climate_districts)].copy()
    if climate_disease!="All categories": cview=cview[cview.Disease.eq(climate_disease)]
    options=[c for c in ["Temp","preci","LAI"] if c in cview and cview[c].notna().any()]
    if cview.empty or not options:
        st.info("Climate fields are not available for the current selection.")
    else:
        field=st.selectbox("Recorded measure",options,format_func=lambda x:CLIMATE_FIELDS[x])
        climate_column="Temperature_C" if field=="Temp" else field
        selected=cview.dropna(subset=[climate_column]).copy()
        selected["Period"]=selected.Date.dt.to_period("M").dt.to_timestamp()
        monthly=selected.groupby("Period",as_index=False).agg(Reported_Cases=("Cases","sum"),Measure=(climate_column,"mean"),Records=("Cases","size"))
        label=CLIMATE_FIELDS[field]
        if len(monthly):
            a,b=st.columns([1.35,1])
            with a:
                st.subheader("Monthly climate readings and case reports")
                fig=px.scatter(monthly,x="Measure",y="Reported_Cases",color=monthly.Period.dt.year.astype(str),hover_data={"Period":True,"Records":True,"Measure":":.2f","Reported_Cases":":,.0f"},color_discrete_sequence=px.colors.qualitative.Safe)
                fig.update_layout(xaxis_title=label,yaxis_title="Reported cases per month",legend_title_text="Year")
                st.plotly_chart(style_chart(fig,410),use_container_width=True)
            with b:
                st.subheader("How both measures changed")
                fig=px.line(monthly,x="Period",y="Reported_Cases",color_discrete_sequence=["#3b8874"],markers=True)
                st.plotly_chart(style_chart(fig,410),use_container_width=True)
                st.caption("Use the dots on the left to compare monthly averages. Each dot represents one calendar month.")
            st.markdown("<div class='soft-note'><b>How to read this:</b> each point combines the selected month’s total case reports with the average recorded climate value in that month. Reporting coverage, seasonality and other factors can affect both measures. This is descriptive analysis, not evidence of causation or a forecast.</div>",unsafe_allow_html=True)
            if field=="Temp":
                st.caption("Temperature is shown in °C, converted from the source notebook’s Kelvin field (Temp − 273.15).")
            elif field=="preci":
                st.caption("The project files do not document the precipitation unit, so the chart uses the source values without assigning a unit.")
            st.metric("Months with both measures recorded",fmt_num(len(monthly)))
        else:
            st.info("No overlapping monthly case and climate readings match these filters.")

elif section == "Awareness & Prevention":
    page_header("PRACTICAL, EVERYDAY GUIDANCE", "Awareness & prevention", "Small, consistent precautions can support community health. Use these general reminders alongside current advice from local public-health authorities.")
    st.markdown("<div class='soft-note'>Season labels below are calendar groupings used in this project to organize historical reports. They are not a prediction of when an individual will become ill.</div>",unsafe_allow_html=True)
    season_details={
        "Summer":{"months":"March – May","tone":"#d99c4e","points":["Drink water from a safe source and take local heat advisories seriously.","Wash hands with soap before eating and while preparing food.","Keep stored water covered and use clean containers."]},
        "Monsoon":{"months":"June – September","tone":"#368674","points":["Use safe drinking water; follow local advice if supplies may be contaminated after flooding.","Empty, cover or clean containers that collect water around homes and shared spaces.","Use mosquito bite prevention such as screens, covering clothing and repellents as directed on the label."]},
        "Post-Monsoon":{"months":"October – November","tone":"#719a61","points":["Continue checking for standing water after rain and keep water storage containers covered.","Keep food and drinking water protected from contamination.","Follow district health advisories and community prevention campaigns."]},
        "Winter":{"months":"December – February","tone":"#6093ad","points":["Maintain hand hygiene and use safe water for drinking and food preparation.","Keep indoor spaces clean and follow local public-health guidance when illness is reported nearby.","Seek professional advice if you feel unwell or are concerned about symptoms."]},
    }
    cols=st.columns(2)
    for idx,season in enumerate(SEASONS):
        info=season_details[season]
        with cols[idx%2]:
            with st.container(border=True):
                st.markdown(f"<div style='color:{info['tone']};font-size:.75rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase'>{season} · {info['months']}</div>",unsafe_allow_html=True)
                st.markdown("\n".join(f"- {point}" for point in info["points"]))
    st.subheader("When to seek professional advice")
    st.write("This website cannot assess symptoms or provide a diagnosis. Contact a qualified healthcare professional for personal health concerns, and seek prompt medical attention if someone feels seriously unwell or their condition worsens. Follow local emergency guidance where needed.")
    st.subheader("Trusted public-health guidance")
    st.markdown("- [WHO: dengue prevention and bite protection](https://www.who.int/health-topics/dengue-and-severe-dengue)\n- [WHO: safe water, sanitation and hygiene during emergencies](https://www.who.int/teams/environment-climate-change-and-health/water-sanitation-and-health/environmental-health-in-emergencies/humanitarian-emergencies)\n- [India NCDC: public-health advisory for floods](https://www.ncdc.mohfw.gov.in/wp-content/uploads/2024/08/Health-impacts-of-Flood-during-Monsoon-season-2024.pdf)\n- [India MoHFW: monsoon preparedness advisory](https://www.ihpoe.mohfw.gov.in/assets/pdf/Revised%20Health%20Advisory%20for%20Monsoon%20Preparedness-05june2024.pdf)")
    st.caption("Advice is general information. Local authorities and qualified health professionals can provide current, situation-specific guidance.")

with st.expander("About the data and how to interpret the charts"):
    st.markdown(f"The preferred file is `Maharashtra_Feature_Engineered.csv`; the dashboard uses its date, disease, case count, district, and available climate fields. Current file: `{data_source}`. The displayed period is **{df.Date.min():%Y}–{df.Date.max():%Y}**.")
    st.markdown("Reported counts are influenced by source coverage and reporting practices. District totals are not adjusted for population. Climate charts show monthly co-occurrence and do not establish causality. This dashboard is for awareness and historical exploration only.")

footer_links=[]
if LINKEDIN_PROFILE_URL.strip():
    footer_links.append(f"<a href='{escape(LINKEDIN_PROFILE_URL, quote=True)}' target='_blank' rel='noopener noreferrer'>LinkedIn ↗</a>")
if CONTACT_EMAIL.strip():
    footer_links.append(f"<a href='mailto:{escape(CONTACT_EMAIL, quote=True)}'>Email</a>")
links_html=f"<div class='footer-links'>{' '.join(footer_links)}</div>" if footer_links else ""
st.markdown(
    f"<div class='footer'><div class='footer-credit'><span class='footer-credit-label'>Created by</span><span class='footer-signature'>Huzaifa Baig</span></div>{links_html}<div class='footer-note'>Historical public-health awareness<br>Not a diagnostic or prediction service</div></div>",
    unsafe_allow_html=True,
)
