from fastapi import FastAPI
from routes import user_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS para conectar frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "API de plataforma fintech operativa"}
