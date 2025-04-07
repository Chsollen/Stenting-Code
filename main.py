from fastapi import FastAPI, Header, HTTPException, Depends

app = FastAPI()

# For demonstration purposes, this is our "valid" API key.
# In production, retrieve this from environment variables or a secrets manager.
VALID_API_KEY = "8fc1b4fd80f5cb3c6e705a1428342c02"

# Dependency to verify the API key sent in request headers
async def verify_api_key(api_key: str = Header(...)):
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

@app.get("/")
async def read_root(api_key: str = Depends(verify_api_key)):
    return {"message": "Hello, this is your secure FastAPI backend!"}

@app.post("/save_annotation")
async def save_annotation(annotation: dict, api_key: str = Depends(verify_api_key)):
    # In a real-world app, save the annotation to a database or file.
    # For now, just echo back the received data.
    return {"status": "saved", "annotation": annotation}
