from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime, timezone
from data_models.upload import ResumeUploadMetadata
from utils.external_resources import S3Client, MongoDBClient
from utils.extract_pdf import PDFExtractor
from agents.evaluation import ResumeScorer, create_default_scoring_criteria

from bson import ObjectId
scorer = ResumeScorer(model_name="gemma3:1b")

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
        upload_time=datetime.now(timezone.utc),
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

#api to process the uploaded resume for evaluation feature
@app.post("/api/process_resume/{resume_id}")
async def process_resume(resume_id: str):
    if not resume_id:
        raise HTTPException(status_code=400, detail="Resume ID is required")
    
    # Fetch metadata from MongoDB
    record = resume_collection.find_one({"_id": resume_id})
    if not record:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Download file from S3
    temp_path = os.path.join("/tmp", record["filename"])
    s3.download_file(BUCKET_NAME, record["filename"], temp_path)

    # result = scorer.score_resume(sample_resume, job_description, scoring_criteria)
    # Extract text from PDF'
    job_description = """
    We're seeking a Senior Data Scientist to join our AI team. 
    Requirements: 3+ years experience, Python, SQL, Machine Learning.
    Preferred: AWS, Docker, team leadership experience.
    """
    extractor = PDFExtractor(temp_path)
    pdf_text = extractor.extract_text()
    scoring_criteria = create_default_scoring_criteria()
    for result in scorer.score_resume(pdf_text, job_description, scoring_criteria):
            print(f"Criteria: {result}")
    result = result["generate_feedback"]
    # Clean up temporary file
    os.remove(temp_path)

    return JSONResponse(content={
        "message": "Resume processed successfully",
        "resume_id": resume_id,
        "extracted_text": pdf_text,
        "result": result

    })