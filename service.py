from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from data_models.upload import ResumeUploadMetadata
from utils.external_resources import S3Client, MongoDBClient
from bson import ObjectId

app = FastAPI()

s3 = S3Client()
mongo = MongoDBClient()
db = mongo.get_database("resume_db")
resume_collection = db["resumes"]

BUCKET_NAME = "resumes"

@app.post("/api/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Save file temporarily
    temp_path = os.path.join("/tmp", file.filename)
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Upload to S3 (MinIO)
    s3.upload_file(temp_path, BUCKET_NAME, file.filename)
    file_size = os.path.getsize(temp_path)
    os.remove(temp_path)

    # Create metadata
    metadata = ResumeUploadMetadata(
        filename=file.filename,
        content_type=file.content_type,
        upload_time=datetime.timezone_aware(),
        file_size=file_size,
        uploader_id=None  # Set uploader_id if available
    )

    # Insert metadata into MongoDB
    record = metadata.model_dump()
    record["_id"] = str(ObjectId())
    resume_collection.insert_one(record)

    return JSONResponse(content={
        "message": "Resume uploaded successfully",
        "filename": file.filename,
        "resume_id": record["_id"]
    })