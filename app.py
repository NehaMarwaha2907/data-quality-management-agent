import streamlit as st
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="Data Quality Agent",
    page_icon="📊",
    layout="wide",
)

# Professional corporate styling
st.markdown(
    """
    <style>
    .stApp {
        background: #F8FAFC;
        color: #172554;
    }
    [data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.92);
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    .hero {
        background: linear-gradient(120deg, #172554 0%, #1D4ED8 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 28px rgba(23, 37, 84, 0.14);
    }
    .hero h1 {
        color: white !important;
        font-size: 2.15rem;
        line-height: 1.2;
        margin: 0 0 0.65rem 0;
        font-weight: 750;
    }
    .hero p {
        color: #DBEAFE !important;
        font-size: 1.05rem;
        margin: 0;
    }
    .section-label {
        color: #172554;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.5rem 0 0.35rem 0;
    }
    .muted {
        color: #64748B;
        font-size: 0.95rem;
    }
    div[data-testid="stFileUploader"] {
        background: white;
        border: 1px solid #DCE5F2;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stDataFrame"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.25rem;
    }
    .status-note {
        background: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        color: #1E3A8A;
        margin: 0.5rem 0 1rem 0;
    }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid #2563EB;
        background: #2563EB;
        color: white;
        font-weight: 600;
        padding: 0.55rem 1rem;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: #1D4ED8;
        border-color: #1D4ED8;
        color: white;
    }
    @media (max-width: 700px) {
        .hero { padding: 1.4rem; }
        .hero h1 { font-size: 1.65rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="hero">
        <h1>Data Quality Management Agent</h1>
        <p>Profile your dataset, spot completeness gaps, and review duplicate records.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Upload section
st.markdown('<div class="section-label">Start with your dataset</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="muted">Upload a CSV or Excel workbook to generate a quick data quality profile.</p>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload CSV or XLSX file",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and Excel (.xlsx).",
)


def load_data(uploaded_file):
    """Read the uploaded file into a Pandas DataFrame."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file type. Please upload CSV or XLSX.")


def profile_data(df):
    """Calculate quality metrics for every column."""
    row_count = len(df)
    profile_rows = []

    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        distinct_count = int(series.nunique(dropna=True))
        missing_pct = missing_count / row_count * 100 if row_count > 0 else 0
        completeness_pct = 100 - missing_pct

        profile_rows.append(
            {
                "column": str(column),
                "data_type": str(series.dtype),
                "row_count": row_count,
                "missing_count": missing_count,
                "missing_pct": round(missing_pct, 2),
                "completeness_pct": round(completeness_pct, 2),
                "distinct_values": distinct_count,
            }
        )

    return pd.DataFrame(profile_rows)


if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        if df.empty:
            st.warning("The file has no data rows.")
            st.stop()

        profile = profile_data(df)
        duplicate_rows = int(df.duplicated().sum())
        total_cells = int(df.shape[0] * df.shape[1])
        missing_cells = int(df.isna().sum().sum())
        overall_completeness = (
            ((total_cells - missing_cells) / total_cells) * 100
            if total_cells > 0
            else 0
        )

        st.markdown(
            '<div class="status-note"><strong>Analysis complete.</strong> Your file was processed successfully.</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-label">Dataset overview</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total rows", f"{len(df):,}")
        col2.metric("Columns", f"{len(df.columns):,}")
        col3.metric("Duplicate rows", f"{duplicate_rows:,}")
        col4.metric("Completeness", f"{overall_completeness:.1f}%")

        st.markdown('<div class="section-label">Column-level data quality</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="muted">Review missing values, completeness, data types, and distinct values for each column.</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(profile, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-label">Dataset preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

        st.download_button(
            "Download profiling report (CSV)",
            data=profile.to_csv(index=False).encode("utf-8"),
            file_name="data_quality_profile.csv",
            mime="text/csv",
        )

    except ImportError as error:
        st.error(
            f"A required package is missing: {error}. "
            "Check that it is listed in requirements.txt and redeploy."
        )
    except Exception as error:
        st.error(f"Unable to process the file: {error}")
else:
    st.markdown(
        """
        <div class="status-note">
            <strong>What you'll get:</strong> row and column counts, duplicate-row count,
            overall completeness, a column-level profile, a dataset preview, and a downloadable report.
        </div>
        """,
        unsafe_allow_html=True,
    )
