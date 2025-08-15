import boto3
from pymongo import MongoClient
from utils.config import settings

class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    def upload_file(self, file_path, bucket_name, object_name):
        self.client.upload_file(file_path, bucket_name, object_name)

    def download_file(self, bucket_name, object_name, file_path):
        self.client.download_file(bucket_name, object_name, file_path)

    def list_buckets(self):
        return self.client.list_buckets()

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(
            settings.mongo_uri,
            username=settings.mongo_username,
            password=settings.mongo_password,
        )

    def get_database(self, db_name):
        return self.client[db_name]

# Usage example in another file:
# from utils.external_resources import S3Client, MongoDBClient
# s3 = S3Client()
# mongo = MongoDBClient()
# s3.upload_file("local.pdf", "mybucket", "resume.pdf")