import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
from routers.cooking import router as cooking_router

app = FastAPI(
    title="SlothFridge API",
    description="The Couch Potato Culinary Copilot for Hacktoberfest Week 3",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cooking_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "SlothFridge Engine"}


if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
