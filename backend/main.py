from fastapi import FastAPI, Depends
from routes import user_routes, auth_routes
from fastapi.middleware.cors import CORSMiddleware
from services.auth_service import get_current_user
from models.user import User

app = FastAPI()

# CORS para conectar frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(user_routes.router, prefix="/api", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "API de plataforma fintech operativa"}

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Protected route", "user": current_user.email}
