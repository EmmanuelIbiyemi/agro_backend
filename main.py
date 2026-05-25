from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Route from auth
from auth.auth_ import auth_router
from modelLLM.LLM_AI import modeling


app.include_router(auth_router)
app.include_router(modeling)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.get("/")
def root():
    return {
        "message": "Welcome to the Agrovision API!",
        "status": "success"
    }
