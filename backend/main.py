# Backend FastAPI Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.core.config import settings
from apps.api.v1.routes import auth, users, stock, watchlist, alerts, positions, market, recommendations

app = FastAPI(
    title="AuraTrade API",
    description="AI 驅動的智能投資分析系統",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(positions.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
# app.include_router(news.router, prefix="/api/v1")  # Temporarily disabled

# Startup Event - Initialize Database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from apps.core.database import init_db
    
    await init_db()
    print("✓ Database initialized successfully")
    
    # TODO: Enable news scheduler after fixing file encoding issues
    # from apps.core.scheduler import news_scheduler
    # news_scheduler.start()
    # print("✓ News scheduler started successfully")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # from apps.core.scheduler import news_scheduler
    # news_scheduler.stop()
    print("✓ Application shutdown")

# Health Check
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "auratrade-backend"}

# Root
@app.get("/")
async def root():
    return {
        "message": "Welcome to AuraTrade API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
