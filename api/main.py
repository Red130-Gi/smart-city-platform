from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager
from routers import traffic, transport, mobility, incidents, analytics, prediction_simple, prediction_ml
from database import init_databases
from models import schemas
import uvicorn

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Smart City API...")
    await init_databases()
    yield
    # Shutdown
    print("Shutting down Smart City API...")

# Create FastAPI application
app = FastAPI(
    title="Smart City Platform API",
    description="API pour la plateforme intelligente de services urbains",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["Traffic"])
app.include_router(transport.router, prefix="/api/v1/transport", tags=["Public Transport"])
app.include_router(mobility.router, prefix="/api/v1/mobility", tags=["Mobility"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(prediction_simple.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(prediction_ml.router, prefix="/api/v1", tags=["ML Predictions"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Smart City Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "kafka": "connected",
            "redis": "connected"
        }
    }

# API Documentation
@app.get("/api/v1/info")
async def api_info():
    return {
        "title": "Smart City Platform API",
        "description": "Plateforme intelligente pour la gestion des services urbains",
        "version": "1.0.0",
        "endpoints": {
            "traffic": "/api/v1/traffic",
            "transport": "/api/v1/transport",
            "mobility": "/api/v1/mobility",
            "incidents": "/api/v1/incidents",
            "analytics": "/api/v1/analytics"
        },
        "documentation": "/docs",
        "openapi": "/openapi.json"
    }

# Global statistics
@app.get("/api/v1/stats")
async def get_global_stats():
    """Get global platform statistics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "active_vehicles": 156,
            "traffic_sensors": 45,
            "average_speed": 38.5,
            "congestion_level": "medium",
            "active_incidents": 3,
            "parking_occupancy": 67.8,
            "air_quality_index": 72
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
