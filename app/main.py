from fastapi import FastAPI
from router.connection_api import router as api_router

# FastAPI App instance create karein
app = FastAPI(title="Mind Web Tree", version="1.0")

# api.py se router ko include/connect karein
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI application! Go to /docs for Swagger UI."}

# Agar aap directly is file ko run karna chahein (python main.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)