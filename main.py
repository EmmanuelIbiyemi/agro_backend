from fastapi import FastAPI

app = FastAPI()

# Route from auth
from agro_backend.auth.auth_ import auth_router
from agro_backend.modelLLM.LLM_AI import modeling


app.include_router(auth_router)
app.include_router(modeling)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Agrovision API!",
        "status": "success"
    }
