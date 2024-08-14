# Image Processing Streamlit App

## Description
A simple Streamlit application that allows users to upload images and process them using two services:

1. **Upscale Image**: Enhance image resolution by a specified factor.
2. **Resize with Bleed**: Resize images to target dimensions with an added bleed margin.

## Features
- **User-Friendly Interface**: Clean and intuitive UI.
- **Image Upload**: Supports JPG and PNG formats.
- **Processing Options**: Upscaling and resizing with bleed.
- **Download**: Retrieve processed images directly.

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/streamlit-app.git
    cd streamlit-app
    ```

2. **Set Up the Environment**
    - *(Optional but recommended)* Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```

3. **Install System Dependencies for Pillow**

   - **macOS**:
     ```bash
     brew install jpeg libtiff little-cms2
     ```

   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get update
     sudo apt-get install libjpeg-dev zlib1g-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl-dev tk-dev
     ```

   - **Windows**:
     Ensure you have the latest versions of pip, setuptools, and wheel:
     ```bash
     python -m pip install --upgrade pip setuptools wheel
     ```

4. **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

    If you encounter issues with Pillow installation, you can try installing Pillow directly with the following command:
    ```bash
    pip install --no-cache-dir --find-links https://files.pythonhosted.org/packages/ Pillow
    ```

## Usage

1. **Run the App**
    ```bash
    streamlit run app.py
    ```

2. **Interact**
    - Open your browser at `http://localhost:8501`.
    - Use the sidebar to upload an image.
    - Select a processing service and set the desired parameters.
    - Click "Process Image" to start processing.
    - Download the processed image once available.

## Dependencies
- streamlit
- requests
- Pillow

*(All dependencies are listed in `requirements.txt`)*

## License
This project is licensed under the MIT License.
