from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.opportunities import router as opportunities_router
from app.api.watchlist import router as watchlist_router

app = FastAPI(title="SteamFlipper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(opportunities_router)
app.include_router(watchlist_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
