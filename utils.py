
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


def calculate_dimensions_with_bleed(initial_width_mm, initial_height_mm, bleed_mm):
    """
    Calculate final dimensions including bleed.
    """
    final_width_mm = initial_width_mm + 2 * bleed_mm
    final_height_mm = initial_height_mm + 2 * bleed_mm
    return final_width_mm, final_height_mm

def calculate_bleed_from_dimensions(initial_width_mm, initial_height_mm, base_width_mm, base_height_mm):
    """
    Calculate bleed based on the difference between base and initial dimensions.
    """
    bleed_width = (base_width_mm - initial_width_mm) / 2
    bleed_height = (base_height_mm - initial_height_mm) / 2
    # Return the larger bleed value to ensure the bleed is uniform around the image
    return max(bleed_width, bleed_height)

def get_initial_dimensions(uploaded_file):
    """
    Get initial dimensions from the image metadata or use defaults.
    """
    if uploaded_file is not None:
        # Assume we can get image dimensions from metadata (replace with actual metadata extraction)
        initial_width_mm = 100  # Replace with actual image width in mm from metadata
        initial_height_mm = 150  # Replace with actual image height in mm from metadata
    else:
        initial_width_mm = 100  # Default width in mm
        initial_height_mm = 150  # Default height in mm
    
    return initial_width_mm, initial_height_mm
