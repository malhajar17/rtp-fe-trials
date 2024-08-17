import streamlit as st
from PIL import Image, ImageDraw

def sidebar_title(title):
    """Function to display the sidebar title."""
    st.sidebar.title(title)

def sidebar_file_uploader(label, file_types):
    """Function to create a file uploader in the sidebar."""
    return st.sidebar.file_uploader(label, type=file_types)

def sidebar_radio(label, options):
    """Function to create a radio button in the sidebar."""
    return st.sidebar.radio(label, options)

def sidebar_slider(label, min_value, max_value, value):
    """Function to create a slider in the sidebar."""
    return st.sidebar.slider(label, min_value=min_value, max_value=max_value, value=value)

def sidebar_number_input(label, min_value):
    """Function to create a number input in the sidebar."""
    return st.sidebar.number_input(label, min_value=min_value)

def main_title(title):
    """Function to display the main title."""
    st.title(title)

def main_subheader(subheader):
    """Function to display the main subheader."""
    st.subheader(subheader)

def display_image(image, caption):
    """Function to display an image with a caption."""
    st.image(image, caption=caption, use_column_width=True)

def display_spinner(text):
    """Function to show a spinner with custom text."""
    return st.spinner(text)

def display_success_message(message):
    """Function to display a success message."""
    st.success(message)

def display_error_message(message):
    """Function to display an error message."""
    st.error(message)

def display_info_message(message):
    """Function to display an info message."""
    st.info(message)

def download_button(label, data, file_name, mime):
    """Function to create a download button."""
    st.download_button(label=label, data=data, file_name=file_name, mime=mime)

def create_checkerboard(width, height, tile_size=30):
    """Create a checkerboard pattern image."""
    checkerboard = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(checkerboard)

    num_tiles_x = width // tile_size
    num_tiles_y = height // tile_size

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            if (x + y) % 2 == 0:
                draw.rectangle(
                    [x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size],
                    fill=(192, 192, 192)
                )

    return checkerboard
