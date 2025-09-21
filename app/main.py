from fastapi import FastAPI
from app.routers import general, cases

app = FastAPI(
    title="Lexi Jagriti Scraper API",
    description="An API to scrape case data from the e-Jagriti portal.",
    version="1.0.0"
)

app.include_router(general.router)
app.include_router(cases.router)

@app.get("/", tags=["Health Check"])
def read_root():
    """Welcome endpoint for the API."""
    return {"status": "ok", "message": "Welcome to the Jagriti Scraper API!"}