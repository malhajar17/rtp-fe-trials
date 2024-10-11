# services/remix_image.py

import streamlit as st
import constants as const
from utils.server_utils import remix_image
import requests

def run():
    # Initialize session state variables
    if 'selected_ratio' not in st.session_state:
        st.session_state.selected_ratio = None
    if 'selected_ratio_api' not in st.session_state:
        st.session_state.selected_ratio_api = None
    if 'width' not in st.session_state:
        st.session_state.width = 200
    if 'height' not in st.session_state:
        st.session_state.height = 200
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = 'AUTO'
    if 'selected_palette' not in st.session_state:
        st.session_state.selected_palette = None
    if 'remix_image' not in st.session_state:
        st.session_state.remix_image = None  # Store the remixed image
    if 'modified_image' not in st.session_state:
        st.session_state.modified_image = None  # Store the modified image
    if 'seed' not in st.session_state:
        st.session_state.seed = 0  # Store the seed value
    if 'returned_prompt' not in st.session_state:
        st.session_state.returned_prompt = ""  # Store the prompt

    def update_ratio(choice):
        st.session_state.selected_ratio = choice
        ratio = const.PROTRAIT_RATIOS.get(choice) or const.LANDSCAPE_RATIOS.get(choice)
        if ratio:
            # Check if it is a portrait ratio
            if const.PROTRAIT_RATIOS.get(choice):
                st.session_state.width = 200  # Fixed width for portrait
                st.session_state.height = int(200 * (ratio[1] / ratio[0]))  # Adjust height for portrait
            else:
                st.session_state.height = 200  # Fixed height for landscape
                st.session_state.width = int(200 * (ratio[0] / ratio[1]))  # Adjust width for landscape
        else:
            st.write("Ratio not found")  # Debugging statement

    st.title("Remix Image")

    # Create columns for layout
    col1, col2, col3 = st.columns([1, 1, 3])

    # Portrait ratios in the first column
    with col1:
        st.markdown('<div class="ratios"><h4>Portrait</h4></div>', unsafe_allow_html=True)
        for label, _ in const.PROTRAIT_RATIOS.items():
            if st.button(label, key=f'portrait_{label}'):
                update_ratio(label)

    # Landscape ratios in the second column
    with col2:
        st.markdown('<div class="ratios"><h4>Landscape</h4></div>', unsafe_allow_html=True)
        for label, _ in const.LANDSCAPE_RATIOS.items():
            if st.button(label, key=f'landscape_{label}'):
                update_ratio(label)

    # Display dynamic rectangle reflecting the selected ratio in the third column
    with col3:
        width = st.session_state.width
        height = st.session_state.height
        selected_ratio = st.session_state.selected_ratio

        st.markdown(f"""
            <div class="ratio-container">
                <div class="ratio-box" style="
                    width:{width}px; 
                    height:{height}px; 
                    background-color: #1e1e1e; 
                    border: 2px solid #fff; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    color: white;">
                    {selected_ratio or "Select a ratio"}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Add style selection
    st.subheader("Select a Style")
    st.session_state.selected_style = st.selectbox("Choose a style:", const.styles)

    # Add color palette selection with demo
    st.subheader("Select a Color Palette")
    palette_choice = st.radio("Choose a color palette:", const.palettes)

    # Display color swatches for the selected palette
    st.markdown("### Color Palette Preview")
    colors = const.palette_colors.get(palette_choice, [])
    swatch_html = "".join([
        f"<div style='display:inline-block;width:30px;height:30px;background-color:{color};margin-right:5px;border-radius:4px;'></div>"
        for color in colors
    ])
    st.markdown(swatch_html, unsafe_allow_html=True)

    # Update selected palette in session state
    st.session_state.selected_palette = palette_choice

    # Add image weight selection
    st.subheader("Image Weight")
    image_weight = st.slider("Set image weight:", 0, 100, 50)

    # Use the already uploaded image from the sidebar
    uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        with open("temp_image.png", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Prompt for remixing the image
        remix_prompt = st.text_area("Enter remix prompt:", "A serene tropical beach scene...")

        # Check if the ratio and prompt are selected and image is uploaded
        if st.session_state.selected_ratio and remix_prompt:
            if st.button("Remix Image"):
                with st.spinner("Remixing your image..."):
                    try:
                        st.session_state.selected_ratio_api = const.aspect_ratio_mapping.get(st.session_state.selected_ratio)

                        if not st.session_state.selected_ratio_api:
                            st.error("Selected aspect ratio is not supported.")
                            raise ValueError("Invalid aspect ratio.")

                        # Call the remix_image function
                        remixed_images = remix_image(
                            "temp_image.png",
                            remix_prompt,
                            st.session_state.selected_ratio_api,
                            st.session_state.selected_style,
                            st.session_state.selected_palette,
                            image_weight,
                            st.secrets["IDEOGRAM_API_KEY"]
                        )

                        # Display and allow download for each remixed image
                        for index, image_data in enumerate(remixed_images):
                            st.write(f"Remixed Image {index + 1} - Resolution: {image_data['resolution']}")
                            st.image(image_data['url'], caption=image_data['prompt'], use_column_width=True)
                            
                            # Download button with a small download icon on top of the image
                            st.download_button(
                                label="⬇️ Download",
                                data=requests.get(image_data['url']).content,
                                file_name=f"remixed_image_{index + 1}.png",
                                mime="image/png"
                            )

                    except ValueError as e:
                        st.error(f"Error: {str(e)}")
