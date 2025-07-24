from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import database
from .auth_routes import router as auth_router
from .task_routes import router as task_router

app = FastAPI(
    title="Task Management API",
    description="FastAPI backend for user and task management with authentication.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Endpoints for user registration and login."},
        {"name": "Tasks", "description": "CRUD operations for user tasks."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure tables are created
    try:
        from .models import Base
        from sqlalchemy import inspect

        engine = database.engine
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables or "users" not in tables or "tasks" not in tables:
            Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Consider logging real error
        print(f"DB setup error: {e}")

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# Routers
app.include_router(auth_router)
app.include_router(task_router)
