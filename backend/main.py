from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# Ensure backend folder is in sys.path
sys.path.append(os.path.dirname(__file__))

from database import init_db
from routes import (
    auth_routes,
    dashboard_routes,
    analytics_routes,
    prediction_routes,
    ai_routes,
    digital_twin_routes,
    report_routes,
    dataset_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Zomato Demo table
    init_db()
    yield

# Initialize FastAPI App
app = FastAPI(
    title="ASTRAL AI-Powered Business Intelligence API",
    description="Enterprise decision-making & predictive BI platform backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(analytics_routes.router)
app.include_router(prediction_routes.router)
app.include_router(ai_routes.router)
app.include_router(digital_twin_routes.router)
app.include_router(report_routes.router)
app.include_router(dataset_routes.router)

# Locate Frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Serve static assets (CSS, JS, assets)
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    if os.path.exists(os.path.join(FRONTEND_DIR, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    # Direct HTML page routes
    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/login")
    def serve_login():
        return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

    @app.get("/analytics")
    def serve_analytics():
        return FileResponse(os.path.join(FRONTEND_DIR, "analytics.html"))

    @app.get("/predictions")
    def serve_predictions():
        return FileResponse(os.path.join(FRONTEND_DIR, "predictions.html"))

    @app.get("/ai-assistant")
    def serve_ai_assistant():
        return FileResponse(os.path.join(FRONTEND_DIR, "ai-assistant.html"))

    @app.get("/digital-twin")
    def serve_digital_twin():
        return FileResponse(os.path.join(FRONTEND_DIR, "digital-twin.html"))

    @app.get("/reports")
    def serve_reports():
        return FileResponse(os.path.join(FRONTEND_DIR, "reports.html"))

    @app.get("/settings")
    def serve_settings():
        return FileResponse(os.path.join(FRONTEND_DIR, "settings.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
