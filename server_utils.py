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
from openai import OpenAI
import json
import constants as const 

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
    

def generate_with_YourDesigner(prompt, aspect_ratio, style, color_palette,seed=-1,magic_prompt_option="AUTO"):

    url = "https://api.ideogram.ai/generate"
    
    if seed == -1:
        payload = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,  # Use the correct aspect ratio format
                "model": "V_2",
                "magic_prompt_option": magic_prompt_option,
                "style": style,
                "color_palette": {
                    "name": color_palette.upper() 
                }
            }
        }
    else:
        payload = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,  # Use the correct aspect ratio format
                "model": "V_2",
                "magic_prompt_option": magic_prompt_option,
                "style": style,
                "seed":seed,
                "color_palette": {
                    "name": color_palette.upper() 
                }
            }
        }
    if color_palette == "None":
        del payload["image_request"]["color_palette"]

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
    return image, image_info['seed'] , image_info['prompt']

def modify_prompt(prompt,modification_prompt):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"), 
        organization='org-l0RJJNv3Mp77MpQPjZyMqubj'
    )
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""You are an assistant that specializes in modifying prompts based on specific instructions. You will receive two pieces of information:

                    1. **Original Prompt**: The initial prompt that needs to be modified.
                    2. **Modification Prompt**: Instructions detailing how to modify the original prompt.

                    **Your Task:**
                    Apply the changes specified in the **Modification Prompt** to the **Original Prompt**. Ensure that only the details mentioned in the modification are altered, and the rest of the original prompt remains exactly the same.

                    **Example:**

                    - **Original Prompt**: "Generate a flyer that has a pink palette, minimalistic, and has the text 'Welcome to Printoclock!!'"
                    - **Modification Prompt**: "Change the text to 'Welcome to our nice company'"
                    - **Result**: "Generate a flyer that has a pink palette, minimalistic, and has the text 'Welcome to our nice company'"

                    **Now, please process the following:**

                    **Original Prompt**: "{prompt}"

                    **Modification Prompt**: "{modification_prompt}"
                """
            }
        ]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.1
    )
    response = completion.choices[0].message.content
        # Split the string by double quotes and take the part in between the first and last quotes

    return response


def describe_image(image_bytes):
    url = "https://api.ideogram.ai/describe"
    files = {"image_file": image_bytes}
    headers = {"Api-Key":  st.secrets["IDEOGRAM_API_KEY"]}

    response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        print(response.json())
        description = response.json().get('descriptions', 'No description found')[0]["text"]
        return description
    else:
        raise ValueError(f"Failed to generate image description: {response.status_code}")

def remix_image(image_file_path, prompt, aspect_ratio, style, color_palette, image_weight, api_key):
    url = "https://api.ideogram.ai/remix"

    # Open the image file directly
    with open(image_file_path, 'rb') as image_file:
        files = {
            'image_file': ('image_file_path', image_file, 'image/png'),  # Use the actual file name and MIME type
        }

        # Prepare the payload inside the 'image_request' wrapper
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,  # Use the correct aspect ratio format
            "model": "V_2",
            "magic_prompt_option": "ON",
            "style": style,
            "image_weight": image_weight,
            "color_palette": {
                "name": color_palette.upper()
            }
        }
        if color_palette == "None":
            del payload["color_palette"]
        # Prepare the form-data
        data = {
            "image_request": json.dumps(payload)  # The payload must be serialized as a string
        }

        headers = {
            "Api-Key": api_key  # No need to specify Content-Type when sending files
        }

        # Send the POST request to the remix API
        response = requests.post(url, data=data, files=files, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")

        response_json = response.json()

        # Check if the response contains the 'data' field
        if 'data' not in response_json or not response_json['data']:
            raise ValueError("No image data found in the response.")

        remixed_images = []
        
        # Iterate through the returned images
        for image_info in response_json['data']:
            image_url = image_info['url']

            # Download each image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise ValueError(f"Failed to download image from {image_url}")

            image = Image.open(BytesIO(image_response.content))

            # Append each image, along with its seed, prompt, and resolution to the list
            remixed_images.append({
                "image": image,
                "seed": image_info['seed'],
                "prompt": image_info['prompt'],
                "resolution": image_info['resolution'],
                "url": image_url
            })

        # Return the list of remixed images
        return remixed_images

import base64
import requests
import os
import streamlit as st

def reimagine_image(image_bytes, selected_ratio, selected_style, selected_palette):
    try:
        # Step 1: Encode the image as base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Prepare the payload to send the base64 image directly
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image for me as one paragraph. I want to give it as a prompt to a diffusion model."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.2
        }

        # Make the request to OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            st.error(f"Failed to get a response from GPT-4o: {response.text}")
            return None, None, None

        # Extract the refined prompt from the response
        refined_prompt = response.json()["choices"][0]["message"]["content"]
        st.write(f"Refined prompt for diffusion model: {refined_prompt}")

    except Exception as e:
        st.error(f"Failed to generate prompt with GPT-4o: {str(e)}")
        return None, None, None

    # Step 2: Generate an image with YourDesigner using the refined prompt
    try:
        # Use the selected aspect ratio, style, and color palette provided in the UI
        reimagined_image, seed, returned_prompt = generate_with_YourDesigner(
            refined_prompt,
            selected_ratio,  # Map the selected ratio to the appropriate API format
            selected_style,
            selected_palette
        )

        # Return the reimagined image, seed, and the refined prompt for future use
        return reimagined_image, seed, returned_prompt

    except Exception as e:
        st.error(f"Failed to generate reimagined image: {str(e)}")
        return None, None, None
