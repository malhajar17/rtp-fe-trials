
import os
import boto3
from PIL import Image
from io import BytesIO

def initialize_s3_client():
    # Initialize the S3 client using environment variables for AWS credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return s3_client

def image_from_s3(bucket, key):
    s3_client = boto3.resource('s3')
    bucket = s3_client.Bucket(bucket)
    image = bucket.Object(key)
    img_data = image.get().get('Body').read()
    return Image.open(BytesIO(img_data))