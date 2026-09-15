import streamlit as st
import httpx
import os
import pandas as pd



BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    rows, offset = [], 0
    while True:
        payload = httpx.get(
            f"{BASE_URL}/lunar/eclipses",
            params={"limit": 100, "offset": offset},
            timeout=30,
        ).json()
        rows += payload["results"]
        offset += 100
        if offset >= payload["total"]:
            return pd.DataFrame(rows)


def main():
    st.set_page_config(page_title="Lunar Eclipse Events", layout="wide")
    st.title("🌘 Lunar Eclipse Events")

    try:
        df = load_data()
    except httpx.HTTPError:
        st.error(f"Could not reach the backend at {BASE_URL}")
        st.stop()

    categories = sorted(df["category"].unique())
    chosen = st.sidebar.multiselect("Category", categories, default=categories)
    year_from, year_to = st.sidebar.slider(
        "Year range", int(df["Year"].min()), int(df["Year"].max()),
        (int(df["Year"].min()), int(df["Year"].max())),
    )

    view = df[df["category"].isin(chosen) & df["Year"].between(year_from, year_to)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Eclipses", f"{len(view):,}")
    col2.metric("Years", f"{year_from} → {year_to}")
    col3.metric("Saros series", view["Saros Number"].nunique())

    if view.empty:
        st.warning("No eclipses match the filters.")
        st.stop()

    left, right = st.columns(2)
    left.subheader("By category")
    left.bar_chart(view["category"].value_counts())

    right.subheader("Per century")
    right.bar_chart(view.groupby((view["Year"] // 100) * 100).size())

    st.subheader("Catalogue")
    st.dataframe(view.head(200), hide_index=True)

    row2_left, row2_right = st.columns(2)

    row2_left.subheader("Per decade")
    per_decade = (
        view.groupby((view["Year"] // 15) * 15).size()
        .rename_axis("Decade").rename("Eclipses")
    )
    row2_left.line_chart(per_decade)

    row2_right.subheader("Average total eclipse duration")
    minutes = pd.to_numeric(view["Total Eclipse Duration (m)"], errors="coerce")
    avg_duration = (
        minutes.groupby((view["Year"] // 100) *100).mean().dropna()
        .rename_axis("Century").rename("Minutes")
    )
    if avg_duration.empty:
        row2_right.info("No total eclipse in this selection")
    else:
        row2_right.line_chart(avg_duration)


if __name__ == "__main__":
    main()