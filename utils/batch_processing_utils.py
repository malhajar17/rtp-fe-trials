# batch_processing_utils.py

import io
import pandas as pd
import os
import tempfile
import zipfile
import shutil
import constants as const
import streamlit as st
from datetime import datetime
import boto3
from utils import server_utils

def initialize_s3_client():
    # Initialize the S3 client with your credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets.get("AWS_REGION", "us-east-1")
    )
    return s3_client

def upload_to_s3(file_path, bucket_name, s3_path, object_name=None, s3_client=None):
    if s3_client is None:
        s3_client = initialize_s3_client()

    if object_name is None:
        object_name = os.path.basename(file_path)
    
    # Construct the full S3 object path
    s3_object_path = os.path.join(s3_path, object_name)
    
    try:
        s3_client.upload_file(file_path, bucket_name, s3_object_path)
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_object_path}"
        return url
    except Exception as e:
        st.error(f"Error uploading to S3: {e}")
        return None

def process_csv_prompts(uploaded_csv, ratio_label, style, palette, username, generation_type):
    # Read the CSV file
    try:
        df = pd.read_csv(uploaded_csv)
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return None

    st.write("CSV File Uploaded Successfully!")
    st.dataframe(df)

    # Standardize column names to lowercase
    df.columns = df.columns.str.lower()

    # Check if 'prompt' column exists
    if 'prompt' not in df.columns:
        st.error("CSV file must contain a 'prompt' column.")
        return None

    # Get the 'prompt' column
    df = df[['prompt']]

    # Get the aspect ratio API value
    ratio_api = const.aspect_ratio_mapping.get(ratio_label)
    if not ratio_api:
        st.error("Selected aspect ratio is not supported.")
        return None

    # Create a temporary directory to store images and mapping CSV
    temp_dir = tempfile.mkdtemp()
    images = []
    mapping = []

    for index, row in df.iterrows():
        prompt = row['prompt']
        if not prompt:
            st.error(f"Row {index}: Missing prompt. Skipping.")
            continue

        # Call generate_with_YourDesigner function
        try:
            image, seed, returned_prompt = server_utils.generate_with_YourDesigner(
                prompt,
                ratio_api,
                style,
                palette
            )
            # Save image to temporary directory
            image_name = f"image_{index}.png"
            image_path = os.path.join(temp_dir, image_name)
            image.save(image_path)
            images.append(image_path)
            # Add to mapping
            mapping.append({
                'original_index': index,
                'prompt': prompt,
                'generated_image': image_name,
                'seed': seed,
                'returned_prompt': returned_prompt,
                'ratio': ratio_label,
                'style': style,
                'palette': palette
            })
        except Exception as e:
            st.error(f"Error processing row {index}: {str(e)}")
            mapping.append({
                'original_index': index,
                'prompt': prompt,
                'error': str(e)
            })

  # Create mapping CSV in the temporary directory
    mapping_df = pd.DataFrame(mapping)
    mapping_csv_path = os.path.join(temp_dir, 'mapping.csv')
    mapping_df.to_csv(mapping_csv_path, index=False)

    # Create zip file in memory (BytesIO) and also on disk for S3 upload
    zip_buffer = io.BytesIO()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    zip_filename = f"{generation_type}_{timestamp}.zip"
    zip_filepath = os.path.join(temp_dir, zip_filename)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file_memory, \
         zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zip_file_disk:
        
        # Add images and CSV to both in-memory and disk zip files
        for image_path in images:
            zip_file_memory.write(image_path, os.path.basename(image_path))
            zip_file_disk.write(image_path, os.path.basename(image_path))
        
        zip_file_memory.write(mapping_csv_path, 'mapping.csv')
        zip_file_disk.write(mapping_csv_path, 'mapping.csv')

    # Move the buffer's position to the beginning so it can be read for download
    zip_buffer.seek(0)

    # Upload ZIP file to S3 from the disk
    bucket_name = st.secrets["S3_BUCKET_NAME"]
    s3_folder = f"users/{username}/history"
    s3_client = initialize_s3_client()
    s3_url = upload_to_s3(zip_filepath, bucket_name, s3_folder, zip_filename, s3_client)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)

    # Return both S3 URL and the in-memory zip buffer for downloading
    history_entry = {
        'timestamp': timestamp,
        's3_url': s3_url,
        'ratio': ratio_label,
        'style': style,
        'palette': palette,
        'filename': zip_filename,
        'generation_type': generation_type
    }

    return history_entry, zip_buffer