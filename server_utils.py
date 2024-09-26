import requests
from PIL import Image
from io import BytesIO
import os 
import streamlit as st
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
    if upscale_factor < 2.000001:
        # Define the payload for upscaling
        payload = {
            "input": {
                "base64_image": base64_image,
                "type": "upscale",
                "model_params": {
                    "upscale_factor": upscale_factor,
                    "aws_save_name": filename,
                    "upscaler_model_name":"RealESRGAN_x2plus",
                    "tile": 0
                },
                
            }
        }
    else:
                # Define the payload for upscaling
        payload = {
            "input": {
                "base64_image": base64_image,
                "type": "upscale",
                "model_params": {
                    "upscale_factor": upscale_factor,
                    "aws_save_name": filename,
                    "upscaler_model_name":"RealESRGAN_x4plus",
                    "tile": 1200
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


def resize_with_bleed(image_bytes, width, height, bleed_w,bleed_h):
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
                "target_resolution": [int(width), int(height)],
                "bleed_size_w": int(bleed_w),
                "bleed_size_h": int(bleed_h),
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
        object_key = f"outpainted-images/{filename}"
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


def generate_flyer_image(prompt):
    # Get the current timestamp and format the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_generated_flyer.png"

    # Define a dummy image URL (since the image_url is not used but required)
    dummy_image_url = "https://cdn-avatars.huggingface.co/v1/production/uploads/639c5c448a34ed9a404a956b/jcypw-eh7JzKHTffd0N9l.jpeg"

    # Define the payload for generating the flyer
    payload = {
        "input": {
            "image_url": dummy_image_url,  # This is just a placeholder
            "type": "generate",
            "model_params": {
                "flux_prompt": prompt,
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
        object_key = f"generated-images/{filename}"
        image = image_from_s3(bucket_name, object_key)
        return image, object_key
    else:
        raise ValueError("Output does not contain a valid image URL")
    

def generate_with_ideogram(prompt, aspect_ratio, style, color_palette):

    url = "https://api.ideogram.ai/generate"

    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,  # Use the correct aspect ratio format
            "model": "V_2",
            "magic_prompt_option": "AUTO",
            "style": style,
            "color_palette": {
                "name": color_palette.upper() 
            }
        }
    }

    headers = {
        "Api-Key": st.secrets["IDEOGRAM_API_KEY"],  # Replace with your actual API key
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")

    response_json = response.json()

    # Check if the response contains the 'data' field
    if 'data' not in response_json or not response_json['data']:
        raise ValueError("No image data found in the response.")

    # Get the first image URL
    image_info = response_json['data'][0]
    image_url = image_info['url']

    # Download the image
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        raise ValueError(f"Failed to download image from {image_url}")

    image = Image.open(BytesIO(image_response.content))

    # Return the image and additional info if needed
    return image, image_info