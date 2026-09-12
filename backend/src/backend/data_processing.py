import pandas as pd
from backend.constants import DATA_PATH

# load data file
df = pd.read_csv(DATA_PATH)

# cleaning missing value
duration_columns = [
    "Penumbral Eclipse Duration (m)",
    "Partial Eclipse Duration (m)",
    "Total Eclipse Duration (m)",
]

df[duration_columns] = df[duration_columns].replace("-", pd.NA)
df["Eclipse Type"] = df["Eclipse Type"].fillna("Unknown")

# create fiealds for the API to filter with
df["Year"] = df["Calendar Date"].str.extract(r"^(-?\d+)").astype(int)

df["category"] = df["Eclipse Type"].map({
    "N": "Penumbral",
    "P": "Partial",
    "T": "Total",
    "T+": "Total",
}).fillna("Unknown")


def to_records(dataframe: pd.DataFrame) -> list[dict]:
    return dataframe.astype(object).where(dataframe.notna(),None).to_dict(orient="records")

def summary(dataframe: pd.DataFrame) -> dict:
    return {
        "total_eclipse": len(dataframe),
        "categories": dataframe["category"].value_counts().to_dict(),
        "year_from": int(dataframe["Year"].min()),
        "year_to": int(dataframe["Year"].max()),
        "saros_series": int(dataframe["Saros Number"].nunique()),
    }