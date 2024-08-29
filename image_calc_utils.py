from PIL import Image
import streamlit as st
import io
import image_calc_utils as img_utils
from server_utils import *

def get_initial_dimensions(image_bytes):
    """
    Get initial dimensions from the image metadata or use defaults.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            width_px, height_px = image.size
            dpi = image.info.get('dpi', (300, 300))
            dpi_x, dpi_y = dpi
            initial_width_mm = (width_px / dpi_x) * 25.4
            initial_height_mm = (height_px / dpi_y) * 25.4
        return initial_width_mm, initial_height_mm
    except Exception as e:
        raise ValueError(f"Failed to get image dimensions: {str(e)}")

def resize_with_bleed_server(image_bytes, width_mm, height_mm, bleed_w_mm, bleed_h_mm, resize_with_bleed_func):
    """
    Calls the server function to resize the image and add bleed.
    """
    resized_image, image_bytes = resize_with_bleed_func(image_bytes, width_mm, height_mm, bleed_w_mm, bleed_h_mm)
    return resized_image, image_bytes

def process_image_smaller_than_format(image_bytes, format_width_mm, format_height_mm, resize_with_bleed_func):
    """
    Process an image that is smaller than the selected format by adding bleed.
    """
    original_width_mm, original_height_mm = get_initial_dimensions(image_bytes)
    bleed_w_mm = (format_width_mm - original_width_mm) / 2
    bleed_h_mm = (format_height_mm - original_height_mm) / 2

    resized_image, image_bytes = resize_with_bleed_server(image_bytes, original_width_mm, original_height_mm, bleed_w_mm, bleed_h_mm, resize_with_bleed_func)
    return resized_image, image_bytes

def process_image_larger_than_format(image_bytes, format_width_mm, format_height_mm, resize_option, resize_with_bleed_func):
    """
    Process an image that is larger than the selected format, allowing for either cropping or resizing with bleed.
    This function maintains the aspect ratio, ensuring the image fills the format without any black bars.
    """
    with Image.open(io.BytesIO(image_bytes)) as image:
        # Ensure the image's DPI is 300
        original_dpi = image.info.get('dpi', (300, 300))
        if original_dpi != (300, 300):
            image = image.resize(image.size, resample=Image.LANCZOS)
            image.info['dpi'] = (300, 300)

        # Convert format dimensions from mm to pixels
        format_width_px = int((format_width_mm / 25.4) * 300)
        format_height_px = int((format_height_mm / 25.4) * 300)

        if resize_option == "Crop Image":
            # Resize the image so that the smaller dimension fits the format
            aspect_ratio_image = image.width / image.height
            aspect_ratio_format = format_width_px / format_height_px

            if aspect_ratio_image > aspect_ratio_format:
                # Image is wider relative to the format, fit height and crop width
                new_height = format_height_px
                new_width = int(new_height * aspect_ratio_image)
            else:
                # Image is taller relative to the format, fit width and crop height
                new_width = format_width_px
                new_height = int(new_width / aspect_ratio_image)

            image = image.resize((new_width, new_height), Image.LANCZOS)

            # Center crop the image to the exact format dimensions
            left = (image.width - format_width_px) / 2
            top = (image.height - format_height_px) / 2
            right = (image.width + format_width_px) / 2
            bottom = (image.height + format_height_px) / 2
            cropped_image = image.crop((left, top, right, bottom))

            # Save the cropped image to bytes
            buffered = io.BytesIO()
            cropped_image.save(buffered, format="PNG", dpi=(300, 300))
            return cropped_image, buffered.getvalue()
        else:
            # Scale down the image to fit within the format while maintaining aspect ratio
            image.thumbnail((format_width_px, format_height_px), Image.LANCZOS)
            diff_w = max(0, format_width_px - image.width)
            diff_h = max(0, format_height_px - image.height)


            buffered = io.BytesIO()
            image.save(buffered, format="PNG", dpi=(300, 300))
            return image, buffered.getvalue()
            # Save the resized image to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="PNG", dpi=(300, 300))
            image_bytes = buffered.getvalue()

            # Add bleed only if the image is smaller than the format
            resized_image, image_bytes = resize_with_bleed_server(image_bytes, image.width, image.height, diff_w / 2, diff_h / 2, resize_with_bleed_func)
            return resized_image, image_bytes

        
def process_and_display_image(img_bytes, width_mm, height_mm):
    """
    Handles the logic for processing the image based on the user-defined width and height.
    """
    original_width_mm, original_height_mm = img_utils.get_initial_dimensions(img_bytes)

    if original_width_mm < width_mm and original_height_mm < height_mm:
        # Image is smaller than the format, add bleed to fill the format
        resized_image, image_bytes = img_utils.process_image_smaller_than_format(img_bytes, width_mm, height_mm, resize_with_bleed)
    else:
        # Image is larger than the format, give the user options
        resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Scale Down and Fill Bleed","Crop Image"])
        resized_image, image_bytes = img_utils.process_image_larger_than_format(img_bytes, width_mm, height_mm, resize_option, resize_with_bleed)

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