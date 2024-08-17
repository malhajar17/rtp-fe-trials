import requests
from PIL import Image
from io import BytesIO
import os 

import time
from datetime import datetime
import runpod
import base64
from utils import *
runpod.api_key = os.environ.get("RUNPOD_API_KEY")

# Define the endpoint ID
endpoint = runpod.Endpoint("vdazldfyhyb2kr")

def upscale_image(service_url, image_bytes, upscale_factor):
    # Convert image bytes to a base64 string
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Get the current timestamp and format the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_upscaled_image.png"

    # Define the payload for upscaling
    payload = {
        "input": {
            "base64_image": base64_image,
            "type": "upscale",
            "model_params": {
                "upscale_factor": upscale_factor,
                "aws_save_name": filename
            },
            
        }
    }

    # Run the request
    endpoint = runpod.Endpoint("vdazldfyhyb2kr")
    run_request = endpoint.run(payload)

    # Check the status of the request
    status = run_request.status()
    while status in ["IN_QUEUE", "IN_PROGRESS"]:
        time.sleep(1)
        status = run_request.status()

    # Get the output
    output = run_request.output()

    # Assuming the output contains the image details
    if 'image' in output and output['image'] is not None:
        bucket_name = "readytoprint-images"
        object_key = f"staging-upscaled-images/{filename}"
        image = image_from_s3(bucket_name, object_key)
        return image, object_key
    else:
        raise ValueError("Output does not contain a valid image URL")
    
def download_image(s3_link):
    s3_response = requests.get(s3_link)
    
    if s3_response.status_code == 200:
        return Image.open(BytesIO(s3_response.content)), s3_response.content
    else:
        return None, None


def resize_with_bleed(image_bytes, width, height, bleed):
    # Convert image bytes to a base64 string
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Get the current timestamp and format the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_outpainted_image.png"

    # Define the payload for resizing with bleed
    payload = {
        "input": {
            "base64_image": base64_image,
            "type": "outpaint",
            "model_params": {
                "target_resolution": [width, height],
                "bleed_size_w": bleed,
                "bleed_size_h": bleed,
                "aws_save_name": filename
            }
        }
    }
    

    # Run the request
    endpoint = runpod.Endpoint("vdazldfyhyb2kr")
    run_request = endpoint.run(payload)

    # Check the status of the request
    status = run_request.status()
    while status in ["IN_QUEUE", "IN_PROGRESS"]:
        time.sleep(1)
        status = run_request.status()

    # Get the output
    output = run_request.output()
    # Assuming the output contains the image details
    if 'image' in output and output['image'] is not None:
        bucket_name = "readytoprint-images"
        object_key = f"staging-outpainted-images/{filename}"
        print(output['image'])
        print(object_key)
        image = image_from_s3(bucket_name, object_key)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        return image, image_bytes
    else:
        raise ValueError("Output does not contain a valid image URL")

def remove_background(image_bytes):
    # Convert image bytes to a base64 string
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Get the current timestamp and format the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_bg_removed_image.png"


    payload = {
            "input": {
                "base64_image": base64_image,
                "type": "remove_bg",
                "model_params": {
                    "aws_save_name": filename
                }
            }
    }

    # Run the request
    endpoint = runpod.Endpoint("vdazldfyhyb2kr")
    run_request = endpoint.run(payload)

    # Check the status of the request
    status = run_request.status()
    while status in ["IN_QUEUE", "IN_PROGRESS"]:
        time.sleep(1)
        status = run_request.status()

    # Get the output
    output = run_request.output()

    # Assuming the output contains the image details
    if 'image' in output and output['image'] is not None:
        bucket_name = "readytoprint-images"
        object_key = f"removed-bg-images/{filename}"
        image = image_from_s3(bucket_name, object_key)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        return image, object_key

    else:
        raise ValueError("Output does not contain a valid image URL")
