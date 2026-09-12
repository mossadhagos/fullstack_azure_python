from fastapi import FastAPI, HTTPException,Query
from backend.data_processing import df, summary, to_records


app = FastAPI(
    title="Lunar Eclipse API",
    description="API for eclipse dataset",
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Lunar APi is running",
        "eclipses": len(df),
    }

@app.get("/lunar/statistics")
async def statistics():
    return summary(df)

@app.get("/lunar/eclipses")
async def eclipses(
        category: str | None = Query(None),
        year_from: int | None = Query(None),
        year_to: int | None = Query(None),
        saros: int | None = Query(None),
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0),
):
    subset = df

    if category is not None:
        subset = subset[subset["category"].str.lower() == category.lower()]

    if year_from is not None:
        subset = subset[subset["year_from"] >= year_from]

    if year_to is not None:
        subset = subset[subset["year_to"] <= year_to]

    if saros is not None:
        subset = subset[subset["Saros Number"] == saros]

    total = len(subset)
    page = subset.iloc[offset: offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": to_records(page),
    }




