from backend.main import app  # or wherever your FastAPI app is defined

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)