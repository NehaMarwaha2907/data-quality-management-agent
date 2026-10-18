
import streamlit as st
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="Data Quality Agent",
    layout="wide"
)

st.title("Data Quality Management Agent")
st.write("Please upload your dataset to begin data analysis.")

# Upload a CSV or Excel file
uploaded_file = st.file_uploader(
    "Upload CSV or XLSX file",
    type=["csv", "xlsx"]
)


def load_data(uploaded_file):
    """Read the uploaded file into a Pandas DataFrame."""

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload CSV or XLSX.")


def profile_data(df):
    """Calculate quality metrics for every column."""

    row_count = len(df)
    profile_rows = []

    for column in df.columns:
        series = df[column]

        missing_count = int(series.isna().sum())
        distinct_count = int(series.nunique(dropna=True))

        if row_count > 0:
            missing_pct = missing_count / row_count * 100
        else:
            missing_pct = 0

        completeness_pct = 100 - missing_pct

        profile_rows.append({
            "column": str(column),
            "data_type": str(series.dtype),
            "row_count": row_count,
            "missing_count": missing_count,
            "missing_pct": round(missing_pct, 2),
            "completeness_pct": round(completeness_pct, 2),
            "distinct_values": distinct_count,
        })

    # Return the profile only after processing every column
    return pd.DataFrame(profile_rows)


# Process the file after the user uploads it
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        if df.empty:
            st.warning("The file has no data rows.")
            st.stop()

        profile = profile_data(df)
        duplicate_rows = int(df.duplicated().sum())

        st.success("File uploaded and processed successfully!")

        # Display summary metrics
        col1, col2, col3 = st.columns(3)

        col1.metric("Rows", f"{len(df):,}")
        col2.metric("Columns", f"{len(df.columns):,}")
        col3.metric("Duplicate rows", f"{duplicate_rows:,}")

        # Display the data quality profile
        st.subheader("Column-Level Data Quality Profile")
        st.dataframe(
            profile,
            use_container_width=True,
            hide_index=True
        )

        # Display sample records
        st.subheader("Dataset Preview")
        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True
        )

        # Allow downloading the report
        st.download_button(
            "Download Profiling Report",
            data=profile.to_csv(index=False).encode("utf-8"),
            file_name="data_quality_profile.csv",
            mime="text/csv"
        )

    except Exception as error:
        st.error(f"Unable to process the file: {error}")
