
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
        # Open the image using PIL
        image = Image.open(uploaded_file)
        
        # Get image dimensions in pixels
        width_px, height_px = image.size
        
        # Attempt to retrieve DPI from image metadata, or assume 300 DPI if not available
        dpi = image.info.get('dpi', (300, 300))
        dpi_x, dpi_y = dpi
        
        # Convert dimensions from pixels to millimeters
        # 1 inch = 25.4 mm
        initial_width_mm = (width_px / dpi_x) * 25.4
        initial_height_mm = (height_px / dpi_y) * 25.4
    else:
        # Default dimensions in millimeters
        initial_width_mm = 0
        initial_height_mm = 0  
    
    return initial_width_mm, initial_height_mm

