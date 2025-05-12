from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.routes import auth_routes, user_routes
from src.infrastructure.database.database import Base, engine
from src.settings import Settings

# Create database tables
Base.metadata.create_all(bind=engine)

settings = Settings()
app = FastAPI(
    title=settings.app_name,
    description="User Management API with FastAPI, SQLite and Hexagonal Architecture",
    version="0.1.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)


@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "User Management API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
