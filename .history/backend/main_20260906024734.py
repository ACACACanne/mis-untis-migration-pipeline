import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Initialize the main FastAPI application engine
app = FastAPI(
    title="MIS to Untis Migration Pipeline API",
    description="API for migrating data from MIS to Untis",
    version="1.0.0"
)

#Configure Cross-Origin Resource Sharing (CORS) settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the MIS to Untis Migration Pipeline API!"}   
    "status": "success",
    "Pipeline": "MIS to Untis Migration",
    "version": "1.0.0"