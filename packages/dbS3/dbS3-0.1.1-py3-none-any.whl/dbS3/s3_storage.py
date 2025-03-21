import json
import logging
import os
import boto3
from tinydb import Storage, TinyDB

class S3Storage(Storage):
    """Class to store database files in S3."""
    def __init__(self, bucket, file):
        self.bucket = bucket
        self.file = file
        self.client = boto3.resource('s3')

    def read(self):
        bucket = self.client.Bucket(self.bucket)
        if len(list(bucket.objects.filter(Prefix=self.file))) > 0:
            logging.info(f"File {self.file} found in S3")
            response = bucket.Object(self.file).get()
            data_str = response['Body'].read().decode('utf-8')

            if not data_str.strip():
                return {}

            return json.loads(data_str)

        logging.info(f"File '{self.file}' not found in S3. Creating the file.")
        bucket.put_object(
            Key=self.file,
            Body=json.dumps({})
        )

    def write(self, data):
        self.client.Object(self.bucket, self.file).put(Body=json.dumps(data))

    def close(self):
        pass

def get_database(file_database: str = "database/hub_poc_data.json"):
    return TinyDB(
        bucket=os.getenv("BUCKET"),
        file=file_database,
        storage=S3Storage
    )