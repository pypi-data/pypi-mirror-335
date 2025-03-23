import boto3
import os
from botocore.exceptions import NoCredentialsError

class S3Manager:
    def __init__(self, bucket_name):
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def upload_file(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            self.s3.upload_file(file_path, self.bucket_name, file_name)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
        except NoCredentialsError:
            print("AWS credentials not found.")
            return None

if __name__ == "__main__":
    s3_manager = S3Manager("your-s3-bucket-name")
    image_url = s3_manager.upload_file("images/sample.png")
    print("Uploaded Image URL:", image_url)
