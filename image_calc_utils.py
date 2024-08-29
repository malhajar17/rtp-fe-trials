from PIL import Image
import streamlit as st
import io
from server_utils import *

def get_initial_dimensions(uploaded_file):
    """
    Get initial dimensions from the image metadata or use defaults.
    """
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        width_px, height_px = image.size
        dpi = image.info.get('dpi', (300, 300))
        dpi_x, dpi_y = dpi
        initial_width_mm = (width_px / dpi_x) * 25.4
        initial_height_mm = (height_px / dpi_y) * 25.4
    else:
        initial_width_mm = 100  
        initial_height_mm = 150  
    
    return initial_width_mm, initial_height_mm

def resize_with_bleed_server(image_bytes, width_mm, height_mm, bleed_w_mm, bleed_h_mm, resize_with_bleed_func):
    """
    Calls the server function to resize the image and add bleed.
    """
    resized_image, image_bytes = resize_with_bleed_func(image_bytes, width_mm, height_mm, bleed_w_mm, bleed_h_mm)
    return resized_image, image_bytes

def process_image_smaller_than_format(image, format_width_mm, format_height_mm, resize_with_bleed_func):
    """
    Process an image that is smaller than the selected format by adding bleed.
    """
    original_width_mm, original_height_mm = get_initial_dimensions(io.BytesIO(image))
    bleed_w_mm = (format_width_mm - original_width_mm) / 2
    bleed_h_mm = (format_height_mm - original_height_mm) / 2

    resized_image, image_bytes = resize_with_bleed_server(image, original_width_mm, original_height_mm, bleed_w_mm, bleed_h_mm, resize_with_bleed_func)
    return resized_image, image_bytes

def process_image_larger_than_format(image_bytes, format_width_mm, format_height_mm, resize_option, resize_with_bleed_func):
    """
    Process an image that is larger than the selected format, allowing for either cropping or resizing with bleed.
    """
    image = Image.open(io.BytesIO(image_bytes))
    original_width_mm, original_height_mm = get_initial_dimensions(io.BytesIO(image_bytes))

    if resize_option == "Crop Image":
        # Resize to fill the format while maintaining aspect ratio, then crop to fit
        image.thumbnail((format_width_mm, format_height_mm))
        left = (image.width - format_width_mm) / 2
        top = (image.height - format_height_mm) / 2
        right = (image.width + format_width_mm) / 2
        bottom = (image.height + format_height_mm) / 2
        cropped_image = image.crop((left, top, right, bottom))

        # Save the cropped image to bytes
        buffered = io.BytesIO()
        cropped_image.save(buffered, format="PNG")
        return cropped_image, buffered.getvalue()
    else:
        # Scale down the image to fit within the format while maintaining aspect ratio and then add bleed
        image.thumbnail((format_width_mm, format_height_mm))
        diff_w = format_width_mm - image.width
        diff_h = format_height_mm - image.height

        resized_image, image_bytes = resize_with_bleed_server(image_bytes, image.width, image.height, diff_w / 2, diff_h / 2, resize_with_bleed_func)
        return resized_image, image_bytes


def process_and_display_image(img_bytes, width_mm, height_mm):
    """
    Handles the logic for processing the image based on the user-defined width and height.
    """
    original_width_mm, original_height_mm = get_initial_dimensions(io.BytesIO(img_bytes))

    if original_width_mm < width_mm and original_height_mm < height_mm:
        # Image is smaller than the format, add bleed to fill the format
        resized_image, image_bytes = process_image_smaller_than_format(img_bytes, width_mm, height_mm, resize_with_bleed)
    else:
        # Image is larger than the format, give the user options
        resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Crop Image", "Scale Down and Fill Bleed"])
        resized_image, image_bytes = process_image_larger_than_format(img_bytes, width_mm, height_mm, resize_option, resize_with_bleed)

    if resized_image:
        st.success("Image processed successfully!")
        st.image(resized_image, caption="Processed Image", use_column_width=True)
        st.download_button(
            label="Download Processed Image",
            data=image_bytes,
            file_name="processed_image.png",
            mime="image/png"
        )
    else:
        st.error("Could not process the image.")
