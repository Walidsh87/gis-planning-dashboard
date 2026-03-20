import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="du GIS Planning Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = os.path.dirname(__file__)
POWER_BI = os.path.join(BASE, "Power Bi")
MAIN = os.path.join(BASE, "Main")

# ─── Color palette ────────────────────────────────────────────────────────────
DU_PURPLE = "#5B2D8E"
DU_GOLD   = "#F5A623"
COLORS = ["#5B2D8E", "#F5A623", "#00AEEF", "#E31837", "#27AE60", "#F39C12", "#8E44AD"]

# ─── Loaders ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_gis_master():
    path = os.path.join(POWER_BI, "GIS Master Site Database_2G_3G_LTE_5G _AUH_AAN_DXB_NE February 2024.xlsx")
    df = pd.read_excel(path, sheet_name="Master Sheet", header=1)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Sitecode"]) if "Sitecode" in df.columns else df
    return df

@st.cache_data(show_spinner=False)
def load_gis_dismantled():
    path = os.path.join(POWER_BI, "GIS Master Site Database_2G_3G_LTE_5G _AUH_AAN_DXB_NE February 2024.xlsx")
    df = pd.read_excel(path, sheet_name="Dismantled Sites", header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_ibs():
    path = os.path.join(POWER_BI, "IBS Master Sheet - GIS Feb 2024.xlsx")
    df = pd.read_excel(path, sheet_name="Sheet1", header=0)
    df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_transport():
    path = os.path.join(POWER_BI, "Transport Database V2.7.xlsx")
    df = pd.read_excel(path, sheet_name="Transport Database V2.1", header=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_mobile_rollout():
    path = os.path.join(BASE, "2024 Mobile Rollout Progress.xlsx")
    df = pd.read_excel(path, sheet_name="OD Jan2024", header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_iib_rollout():
    path = os.path.join(MAIN, "IIB Rollout 2024.xlsx")
    df = pd.read_excel(path, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_osp():
    path = os.path.join(BASE, "OSP 2024.xlsx")
    df = pd.read_excel(path, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_iib_scope():
    path = os.path.join(POWER_BI, "IIB Imp 2024 scope.xlsx")
    df = pd.read_excel(path, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_ne_osp():
    path = os.path.join(POWER_BI, "NE OSP EPOC TRS Plan 2024.xlsx")
    df = pd.read_excel(path, sheet_name="Sheet1", header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_dxb_osp():
    path = os.path.join(POWER_BI, "Copy of DXB - OSP 2024 Final Compiled List - Ahmed AlMazam 29 Jan 2024 Nassar Updated.xlsx")
    df = pd.read_excel(path, sheet_name="Sheet1", header=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_auh_odibs():
    path = os.path.join(POWER_BI, "AUH ODIBS list 2024 scope (22-01-2024) v1.3.xlsx")
    df = pd.read_excel(path, sheet_name="Sheet2", header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(show_spinner=False)
def load_iib_scope_progress():
    path = os.path.join(BASE, "2024 IIB Scope Progress.xlsx")
    xl = pd.ExcelFile(path)
    return {s: pd.read_excel(path, sheet_name=s) for s in xl.sheet_names}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def kpi(col, label, value, color=DU_PURPLE, suffix=""):
    col.markdown(
        f"""<div style="background:{color};border-radius:12px;padding:16px 20px;text-align:center;">
        <div style="color:#fff;font-size:13px;opacity:.8;margin-bottom:4px">{label}</div>
        <div style="color:#fff;font-size:30px;font-weight:700">{value}{suffix}</div></div>""",
        unsafe_allow_html=True,
    )

def clean_map(df, lat_col="Latitude", lon_col="Longitude"):
    df = df.copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    df = df[(df[lat_col].between(22, 27)) & (df[lon_col].between(51, 57))]
    return df

def value_counts_fig(series, title, top_n=15):
    vc = series.dropna().value_counts().head(top_n).reset_index()
    vc.columns = ["Category", "Count"]
    fig = px.bar(vc, x="Count", y="Category", orientation="h", title=title,
                 color="Count", color_continuous_scale=["#D8BFD8", DU_PURPLE])
    fig.update_layout(showlegend=False, coloraxis_showscale=False,
                      yaxis={"categoryorder": "total ascending"}, height=400,
                      margin=dict(l=0, r=0, t=40, b=0))
    return fig

def pie_fig(series, title):
    vc = series.dropna().value_counts().reset_index()
    vc.columns = ["Category", "Count"]
    fig = px.pie(vc, names="Category", values="Count", title=title,
                 color_discrete_sequence=COLORS, hole=0.4)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=350)
    return fig

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1A0A33; }
[data-testid="stSidebar"] * { color: #EEE !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 14px; padding: 4px 0; }
h1, h2, h3 { color: #5B2D8E; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/9/97/Du_telecom.svg/200px-Du_telecom.svg.png",
                 width=120)
st.sidebar.markdown("## GIS Planning 2024")
st.sidebar.markdown("---")

PAGES = {
    "📊 Overview": "overview",
    "📡 GIS Site Database": "gis",
    "📶 IBS Sites": "ibs",
    "🚌 Transport Network": "transport",
    "📱 Mobile Rollout": "mobile",
    "🔗 IIB Rollout": "iib",
    "🌐 OSP 2024": "osp",
    "🏙 AUH ODIBS": "auh",
    "🗺 NE OSP Plan": "ne_osp",
    "🏢 DXB OSP Plan": "dxb_osp",
}

page = st.sidebar.radio("Navigation", list(PAGES.keys()))
page_id = PAGES[page]

st.sidebar.markdown("---")
st.sidebar.markdown("<small>du GIS Planning · Jan–Jul 2024</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page_id == "overview":
    st.title("du GIS Planning Dashboard — 2024 Overview")

    with st.spinner("Loading all datasets…"):
        gis   = load_gis_master()
        mob   = load_mobile_rollout()
        iib   = load_iib_rollout()
        osp   = load_osp()
        ibs   = load_ibs()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Active Sites", f"{len(gis):,}", DU_PURPLE)
    kpi(c2, "Mobile Rollout Sites", f"{len(mob):,}", DU_GOLD)
    kpi(c3, "IIB Rollout Items", f"{len(iib):,}", "#00AEEF")
    kpi(c4, "OSP Projects", f"{len(osp):,}", "#E31837")
    kpi(c5, "IBS Sites", f"{len(ibs):,}", "#27AE60")

    st.markdown("---")
    col1, col2 = st.columns(2)

    # Sites by Region
    if "Region" in gis.columns:
        with col1:
            st.plotly_chart(value_counts_fig(gis["Region"], "GIS Sites by Region"), use_container_width=True)
    # 2G/3G/4G/5G status breakdown
    status_cols = [c for c in ["2G Site Status", "3G Site Status", "4G Site Status", "5G Status"] if c in gis.columns]
    if status_cols:
        with col2:
            rows = []
            for sc in status_cols:
                vc = gis[sc].value_counts()
                for status, cnt in vc.items():
                    rows.append({"Technology": sc.replace(" Site Status", "").replace(" Status", ""), "Status": str(status), "Count": cnt})
            sdf = pd.DataFrame(rows)
            fig = px.bar(sdf, x="Technology", y="Count", color="Status",
                         title="Site Status by Technology", color_discrete_sequence=COLORS,
                         barmode="stack")
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Map of all sites
    st.subheader("Site Map — GIS Master Database")
    map_df = clean_map(gis)
    if not map_df.empty:
        color_col = "Region" if "Region" in map_df.columns else None
        fig_map = px.scatter_mapbox(
            map_df.head(5000), lat="Latitude", lon="Longitude",
            color=color_col, hover_data=["Sitecode"] if "Sitecode" in map_df.columns else None,
            zoom=6, height=500, mapbox_style="carto-positron",
            color_discrete_sequence=COLORS,
            title="du Network Sites — UAE"
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    # IIB Region breakdown
    col3, col4 = st.columns(2)
    if "Region" in iib.columns:
        with col3:
            st.plotly_chart(pie_fig(iib["Region"], "IIB Rollout by Region"), use_container_width=True)
    if "AE Implementation status" in iib.columns:
        with col4:
            st.plotly_chart(pie_fig(iib["AE Implementation status"], "IIB Implementation Status"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GIS SITE DATABASE
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "gis":
    st.title("📡 GIS Master Site Database")
    tab1, tab2, tab3 = st.tabs(["Active Sites", "Dismantled Sites", "Site Map"])

    with tab1:
        gis = load_gis_master()
        c1, c2, c3 = st.columns(3)
        regions = ["All"] + sorted(gis["Region"].dropna().unique().tolist()) if "Region" in gis.columns else ["All"]
        reg_filter = c1.selectbox("Region", regions)
        techs = ["All", "2G", "3G", "4G", "5G"]
        tech_filter = c2.selectbox("Technology Filter", techs)
        search = c3.text_input("Search Site Code")

        fdf = gis.copy()
        if reg_filter != "All" and "Region" in fdf.columns:
            fdf = fdf[fdf["Region"] == reg_filter]
        if search and "Sitecode" in fdf.columns:
            fdf = fdf[fdf["Sitecode"].astype(str).str.contains(search, case=False, na=False)]

        st.markdown(f"**{len(fdf):,} sites** · {fdf['Region'].nunique() if 'Region' in fdf.columns else '—'} regions")

        # Charts
        col1, col2 = st.columns(2)
        if "Region" in fdf.columns:
            with col1:
                st.plotly_chart(value_counts_fig(fdf["Region"], "Sites by Region"), use_container_width=True)
        status_col = "4G Site Status" if "4G Site Status" in fdf.columns else None
        if status_col:
            with col2:
                st.plotly_chart(pie_fig(fdf[status_col], "4G Site Status"), use_container_width=True)

        st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=400)

    with tab2:
        dis = load_gis_dismantled()
        st.markdown(f"**{len(dis):,} dismantled sites**")
        col1, col2 = st.columns(2)
        if "Region" in dis.columns:
            with col1:
                st.plotly_chart(pie_fig(dis["Region"], "Dismantled Sites by Region"), use_container_width=True)
        if "2G Site Status" in dis.columns:
            with col2:
                st.plotly_chart(pie_fig(dis["2G Site Status"], "2G Status of Dismantled Sites"), use_container_width=True)
        st.dataframe(dis, use_container_width=True)

    with tab3:
        gis = load_gis_master()
        map_df = clean_map(gis)
        color_col = "Region" if "Region" in map_df.columns else None
        status_filter = "All"
        if "4G Site Status" in map_df.columns:
            opts = ["All"] + sorted(map_df["4G Site Status"].dropna().unique().tolist())
            status_filter = st.selectbox("Filter by 4G Status", opts)
            if status_filter != "All":
                map_df = map_df[map_df["4G Site Status"] == status_filter]
        fig = px.scatter_mapbox(
            map_df.head(5000), lat="Latitude", lon="Longitude", color=color_col,
            hover_data=["Sitecode"] if "Sitecode" in map_df.columns else None,
            zoom=6, height=600, mapbox_style="carto-positron",
            color_discrete_sequence=COLORS,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: IBS
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "ibs":
    st.title("📶 IBS Master Sheet — Feb 2024")
    ibs = load_ibs()

    c1, c2, c3 = st.columns(3)
    kpi(c1, "Total IBS Sites", f"{len(ibs):,}", DU_PURPLE)
    on_air = ibs[ibs.get("IBS Site Status", pd.Series()).astype(str).str.lower() == "on air"] if "IBS Site Status" in ibs.columns else pd.DataFrame()
    kpi(c2, "On Air", f"{len(on_air):,}", "#27AE60")
    if "Emirates" in ibs.columns:
        kpi(c3, "Emirates", f"{ibs['Emirates'].nunique():,}", DU_GOLD)

    st.markdown("---")
    col1, col2 = st.columns(2)

    if "IBS Site Status" in ibs.columns:
        with col1:
            st.plotly_chart(pie_fig(ibs["IBS Site Status"], "IBS Site Status"), use_container_width=True)
    if "IBS Site Type" in ibs.columns:
        with col2:
            st.plotly_chart(value_counts_fig(ibs["IBS Site Type"], "IBS Site Type"), use_container_width=True)

    col3, col4 = st.columns(2)
    if "Region" in ibs.columns:
        with col3:
            st.plotly_chart(value_counts_fig(ibs["Region"], "Sites by Region"), use_container_width=True)
    if "Emirates" in ibs.columns:
        with col4:
            st.plotly_chart(pie_fig(ibs["Emirates"], "Sites by Emirate"), use_container_width=True)

    # Map
    lat_col = "Lat" if "Lat" in ibs.columns else "Latitude"
    lon_col = "Long" if "Long" in ibs.columns else "Longitude"
    if lat_col in ibs.columns and lon_col in ibs.columns:
        map_df = clean_map(ibs, lat_col, lon_col)
        if not map_df.empty:
            st.subheader("IBS Site Map")
            color_c = "IBS Site Status" if "IBS Site Status" in map_df.columns else None
            hover_c = ["2G  Site Code", "Site Name"] if "Site Name" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat=lat_col, lon=lon_col, color=color_c,
                                    hover_data=hover_c, zoom=6, height=500,
                                    mapbox_style="carto-positron", color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(ibs, use_container_width=True, height=350)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "transport":
    st.title("🚌 Transport Network Database V2.7")
    trn = load_transport()

    c1, c2, c3 = st.columns(3)
    kpi(c1, "Total Sites", f"{len(trn):,}", DU_PURPLE)
    if "Region" in trn.columns:
        kpi(c2, "Regions", f"{trn['Region'].nunique():,}", DU_GOLD)
    if "TRx Media" in trn.columns:
        kpi(c3, "TRx Types", f"{trn['TRx Media'].nunique():,}", "#00AEEF")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "Region" in trn.columns:
        with col1:
            st.plotly_chart(value_counts_fig(trn["Region"], "Sites by Region"), use_container_width=True)
    if "TRx Media" in trn.columns:
        with col2:
            st.plotly_chart(pie_fig(trn["TRx Media"], "TRx Media Distribution"), use_container_width=True)

    col3, col4 = st.columns(2)
    if "Site Type" in trn.columns:
        with col3:
            st.plotly_chart(value_counts_fig(trn["Site Type"], "Site Types"), use_container_width=True)
    if "Device" in trn.columns:
        with col4:
            st.plotly_chart(value_counts_fig(trn["Device"], "Device Types"), use_container_width=True)

    # Map
    if "Latitude" in trn.columns and "Longitude" in trn.columns:
        map_df = clean_map(trn)
        if not map_df.empty:
            st.subheader("Transport Site Map")
            color_c = "TRx Media" if "TRx Media" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Site code"] if "Site code" in map_df.columns else None,
                                    zoom=6, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    reg_f = st.selectbox("Filter Region", ["All"] + (sorted(trn["Region"].dropna().unique().tolist()) if "Region" in trn.columns else []))
    fdf = trn if reg_f == "All" else trn[trn["Region"] == reg_f]
    st.dataframe(fdf, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MOBILE ROLLOUT
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "mobile":
    st.title("📱 Mobile Rollout Progress — 2024")
    mob = load_mobile_rollout()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Sites", f"{len(mob):,}", DU_PURPLE)
    if "Region" in mob.columns:
        kpi(c2, "Regions", f"{mob['Region'].nunique():,}", DU_GOLD)
    if "Vendor" in mob.columns:
        kpi(c3, "Vendors", f"{mob['Vendor'].nunique():,}", "#00AEEF")
    if "5G Logical ID" in mob.columns:
        g5 = mob["5G Logical ID"].notna().sum()
        kpi(c4, "5G Sites", f"{g5:,}", "#E31837")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "Region" in mob.columns:
        with col1:
            st.plotly_chart(value_counts_fig(mob["Region"], "Sites by Region"), use_container_width=True)
    if "2G Site Status" in mob.columns:
        with col2:
            st.plotly_chart(pie_fig(mob["2G Site Status"], "2G Site Status"), use_container_width=True)

    col3, col4 = st.columns(2)
    if "Vendor" in mob.columns:
        with col3:
            st.plotly_chart(pie_fig(mob["Vendor"], "Vendor Distribution"), use_container_width=True)
    if "TRS Media" in mob.columns:
        with col4:
            st.plotly_chart(pie_fig(mob["TRS Media"], "TRS Media Types"), use_container_width=True)

    # Integration timeline
    if "Integration Date" in mob.columns:
        st.subheader("Integration Timeline")
        td = mob.copy()
        td["Integration Date"] = pd.to_datetime(td["Integration Date"], errors="coerce")
        td = td.dropna(subset=["Integration Date"])
        td["Month"] = td["Integration Date"].dt.to_period("M").astype(str)
        monthly = td.groupby("Month").size().reset_index(name="Count")
        fig = px.bar(monthly, x="Month", y="Count", title="Sites Integrated per Month",
                     color="Count", color_continuous_scale=["#D8BFD8", DU_PURPLE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Map
    if "Latitude" in mob.columns and "Longitude" in mob.columns:
        map_df = clean_map(mob)
        if not map_df.empty:
            st.subheader("Rollout Site Map")
            color_c = "Region" if "Region" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Sitecode"] if "Sitecode" in map_df.columns else None,
                                    zoom=6, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(mob, use_container_width=True, height=350)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: IIB ROLLOUT
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "iib":
    st.title("🔗 IIB Rollout 2024")
    tab1, tab2 = st.tabs(["IIB Rollout", "IIB Scope"])

    def render_iib(df, label):
        c1, c2, c3, c4 = st.columns(4)
        kpi(c1, f"{label} Items", f"{len(df):,}", DU_PURPLE)
        if "Region" in df.columns:
            kpi(c2, "Regions", f"{df['Region'].nunique():,}", DU_GOLD)
        if "CSG Type" in df.columns:
            kpi(c3, "CSG Types", f"{df['CSG Type'].nunique():,}", "#00AEEF")
        if "AE Implementation status" in df.columns:
            done = df[df["AE Implementation status"].astype(str).str.lower().str.contains("done|complete|finish", na=False)]
            kpi(c4, "Completed", f"{len(done):,}", "#27AE60")

        st.markdown("---")
        col1, col2 = st.columns(2)
        if "Region" in df.columns:
            with col1:
                st.plotly_chart(value_counts_fig(df["Region"], "Items by Region"), use_container_width=True)
        if "AE Implementation status" in df.columns:
            with col2:
                st.plotly_chart(pie_fig(df["AE Implementation status"], "Implementation Status"), use_container_width=True)

        col3, col4 = st.columns(2)
        if "CSG Type" in df.columns:
            with col3:
                st.plotly_chart(value_counts_fig(df["CSG Type"], "CSG Type Distribution"), use_container_width=True)
        if "Migration Status" in df.columns:
            with col4:
                st.plotly_chart(pie_fig(df["Migration Status"], "Migration Status"), use_container_width=True)

        # RFS Timeline
        if "RFS Date" in df.columns:
            st.subheader("RFS Timeline")
            td = df.copy()
            td["RFS Date"] = pd.to_datetime(td["RFS Date"], errors="coerce")
            td = td.dropna(subset=["RFS Date"])
            td["Month"] = td["RFS Date"].dt.to_period("M").astype(str)
            monthly = td.groupby("Month").size().reset_index(name="Count")
            fig = px.bar(monthly, x="Month", y="Count", title="RFS Dates per Month",
                         color="Count", color_continuous_scale=["#D8BFD8", DU_PURPLE])
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # Map
        if "Latitude" in df.columns and "Longitude" in df.columns:
            map_df = clean_map(df)
            if not map_df.empty:
                st.subheader("Site Map")
                color_c = "AE Implementation status" if "AE Implementation status" in map_df.columns else None
                fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                        hover_data=["Site Code"] if "Site Code" in map_df.columns else None,
                                        zoom=6, height=500, mapbox_style="carto-positron",
                                        color_discrete_sequence=COLORS)
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Data Table")
        region_f = st.selectbox(f"Filter Region ({label})", ["All"] + (sorted(df["Region"].dropna().unique().tolist()) if "Region" in df.columns else []), key=label)
        fdf = df if region_f == "All" else df[df["Region"] == region_f]
        st.dataframe(fdf, use_container_width=True, height=400)

    with tab1:
        render_iib(load_iib_rollout(), "IIB Rollout")
    with tab2:
        render_iib(load_iib_scope(), "IIB Scope")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OSP 2024
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "osp":
    st.title("🌐 OSP Projects — 2024")
    osp = load_osp()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Projects", f"{len(osp):,}", DU_PURPLE)
    if "Region" in osp.columns:
        kpi(c2, "Regions", f"{osp['Region'].nunique():,}", DU_GOLD)
    if "Project Status" in osp.columns:
        kpi(c3, "Status Types", f"{osp['Project Status'].nunique():,}", "#00AEEF")
    if "Vendor" in osp.columns:
        kpi(c4, "Vendors", f"{osp['Vendor'].nunique():,}", "#E31837")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "Region" in osp.columns:
        with col1:
            st.plotly_chart(value_counts_fig(osp["Region"], "Projects by Region"), use_container_width=True)
    if "Project Status" in osp.columns:
        with col2:
            st.plotly_chart(pie_fig(osp["Project Status"], "Project Status"), use_container_width=True)

    col3, col4 = st.columns(2)
    if "TRS Media" in osp.columns:
        with col3:
            st.plotly_chart(pie_fig(osp["TRS Media"], "TRS Media Types"), use_container_width=True)
    if "Project Type" in osp.columns:
        with col4:
            st.plotly_chart(value_counts_fig(osp["Project Type"], "Project Types"), use_container_width=True)

    # Distance analysis
    dist_cols = [c for c in ["ActualProjectDistance_Fiber", "ProposedProjectDistance_Fiber",
                              "ActualProjectDistance_Civil", "ProposedProjectDistance_Civil"] if c in osp.columns]
    if dist_cols:
        st.subheader("Distance Analysis")
        dd = osp[dist_cols].apply(pd.to_numeric, errors="coerce")
        totals = dd.sum().reset_index()
        totals.columns = ["Metric", "Total (m)"]
        totals["Total (km)"] = (totals["Total (m)"] / 1000).round(1)
        fig = px.bar(totals, x="Metric", y="Total (km)", title="Total Distance by Type (km)",
                     color="Metric", color_discrete_sequence=COLORS)
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Map
    if "Latitude" in osp.columns and "Longitude" in osp.columns:
        map_df = clean_map(osp)
        if not map_df.empty:
            st.subheader("OSP Site Map")
            color_c = "Project Status" if "Project Status" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Project Name"] if "Project Name" in map_df.columns else None,
                                    zoom=6, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    reg_f2 = st.selectbox("Filter Region", ["All"] + (sorted(osp["Region"].dropna().unique().tolist()) if "Region" in osp.columns else []))
    fdf = osp if reg_f2 == "All" else osp[osp["Region"] == reg_f2]
    st.dataframe(fdf, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUH ODIBS
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "auh":
    st.title("🏙 AUH ODIBS List 2024")
    auh = load_auh_odibs()

    c1, c2, c3 = st.columns(3)
    kpi(c1, "Total Sites", f"{len(auh):,}", DU_PURPLE)
    if "OSP Scope status" in auh.columns:
        kpi(c2, "Scope Statuses", f"{auh['OSP Scope status'].nunique():,}", DU_GOLD)
    if "Cost" in auh.columns:
        total_cost = pd.to_numeric(auh["Cost"], errors="coerce").sum()
        kpi(c3, "Total Cost (AED)", f"{total_cost:,.0f}", "#E31837")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "OSP Scope status" in auh.columns:
        with col1:
            st.plotly_chart(pie_fig(auh["OSP Scope status"], "OSP Scope Status"), use_container_width=True)
    if "OSP Status" in auh.columns:
        with col2:
            st.plotly_chart(pie_fig(auh["OSP Status"], "OSP Status"), use_container_width=True)

    # Map
    if "Latitude" in auh.columns and "Longitude" in auh.columns:
        map_df = clean_map(auh)
        if not map_df.empty:
            st.subheader("AUH ODIBS Site Map")
            color_c = "OSP Scope status" if "OSP Scope status" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Site Code"] if "Site Code" in map_df.columns else None,
                                    zoom=8, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(auh, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: NE OSP
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "ne_osp":
    st.title("🗺 Northern Emirates OSP Plan 2024")
    ne = load_ne_osp()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Projects", f"{len(ne):,}", DU_PURPLE)
    if "Rollout Status" in ne.columns:
        kpi(c2, "Statuses", f"{ne['Rollout Status'].nunique():,}", DU_GOLD)
    if "OSP cost" in ne.columns:
        total_cost = pd.to_numeric(ne["OSP cost"], errors="coerce").sum()
        kpi(c3, "Total Cost (AED)", f"{total_cost:,.0f}", "#E31837")
    if "2024 plan" in ne.columns:
        kpi(c4, "2024 Plan Items", f"{ne['2024 plan'].notna().sum():,}", "#00AEEF")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "Rollout Status" in ne.columns:
        with col1:
            st.plotly_chart(pie_fig(ne["Rollout Status"], "Rollout Status"), use_container_width=True)
    if "Project Stream" in ne.columns:
        with col2:
            st.plotly_chart(value_counts_fig(ne["Project Stream"], "Project Streams"), use_container_width=True)

    col3, col4 = st.columns(2)
    if "Existing Media" in ne.columns:
        with col3:
            st.plotly_chart(pie_fig(ne["Existing Media"], "Existing Media Types"), use_container_width=True)
    if "2024 plan" in ne.columns:
        with col4:
            st.plotly_chart(value_counts_fig(ne["2024 plan"], "2024 Plan Category"), use_container_width=True)

    # Map
    if "Latitude" in ne.columns and "Longitude" in ne.columns:
        map_df = clean_map(ne)
        if not map_df.empty:
            st.subheader("NE OSP Site Map")
            color_c = "Rollout Status" if "Rollout Status" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Site Code", "Site Name"] if "Site Name" in map_df.columns else None,
                                    zoom=7, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # Cost by project scope
    if "Project Scope" in ne.columns and "OSP cost" in ne.columns:
        st.subheader("Cost Analysis by Project Scope")
        cost_df = ne.copy()
        cost_df["OSP cost"] = pd.to_numeric(cost_df["OSP cost"], errors="coerce")
        scope_cost = cost_df.groupby("Project Scope")["OSP cost"].sum().reset_index().sort_values("OSP cost", ascending=False)
        fig = px.bar(scope_cost, x="Project Scope", y="OSP cost", title="Total OSP Cost by Scope (AED)",
                     color="OSP cost", color_continuous_scale=["#D8BFD8", DU_PURPLE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(ne, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DXB OSP
# ══════════════════════════════════════════════════════════════════════════════
elif page_id == "dxb_osp":
    st.title("🏢 Dubai OSP Final Compiled List 2024")
    dxb = load_dxb_osp()

    c1, c2, c3 = st.columns(3)
    kpi(c1, "Total Projects", f"{len(dxb):,}", DU_PURPLE)
    if "Status" in dxb.columns:
        kpi(c2, "Statuses", f"{dxb['Status'].nunique():,}", DU_GOLD)
    if "Cost" in dxb.columns:
        total_cost = pd.to_numeric(dxb["Cost"], errors="coerce").sum()
        kpi(c3, "Total Cost (AED)", f"{total_cost:,.0f}", "#E31837")

    st.markdown("---")
    col1, col2 = st.columns(2)
    if "Status" in dxb.columns:
        with col1:
            st.plotly_chart(pie_fig(dxb["Status"], "Project Status"), use_container_width=True)
    if "Site Type" in dxb.columns:
        with col2:
            st.plotly_chart(pie_fig(dxb["Site Type"], "Site Type"), use_container_width=True)

    # Map
    if "Latitude" in dxb.columns and "Longitude" in dxb.columns:
        map_df = clean_map(dxb)
        if not map_df.empty:
            st.subheader("DXB OSP Site Map")
            color_c = "Status" if "Status" in map_df.columns else None
            fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color=color_c,
                                    hover_data=["Sitecode"] if "Sitecode" in map_df.columns else None,
                                    zoom=9, height=500, mapbox_style="carto-positron",
                                    color_discrete_sequence=COLORS)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # EPOC breakdown
    if "EPOC" in dxb.columns:
        st.subheader("Sites by EPOC")
        st.plotly_chart(value_counts_fig(dxb["EPOC"], "Sites by EPOC"), use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(dxb, use_container_width=True, height=400)
