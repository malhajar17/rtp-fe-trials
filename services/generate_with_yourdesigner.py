# services/generate_with_yourdesigner.py

import io
import streamlit as st
import constants as const
from io import BytesIO
from utils.server_utils import generate_with_YourDesigner, modify_prompt
from utils.batch_processing_utils import process_csv_prompts
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
    if 'YourDesigner_image' not in st.session_state:
        st.session_state.YourDesigner_image = None  # Store the generated YourDesigner
    if 'modified_image' not in st.session_state:
        st.session_state.modified_image = None  # Store the modified image
    if 'seed' not in st.session_state:
        st.session_state.seed = 0  # Store the seed
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

    st.title("Generate with YourDesigner")

    # Add processing mode selection
    processing_mode = st.radio("Select Processing Mode", ["Single Prompt", "Batch Processing via CSV"])

    if processing_mode == "Single Prompt":

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

        # Prompting user to generate YourDesigner
        YourDesigner_prompt = st.text_area("Enter your YourDesigner prompt here:", "Your YourDesigner content goes here.")

        # Check if the ratio and prompt are selected
        if st.session_state.selected_ratio and YourDesigner_prompt:
            if st.button("Generate YourDesigner"):
                with st.spinner("Generating your YourDesigner..."):
                    try:
                        st.session_state.selected_ratio_api = const.aspect_ratio_mapping.get(st.session_state.selected_ratio)

                        if not st.session_state.selected_ratio_api:
                            st.error("Selected aspect ratio is not supported.")
                            raise ValueError("Invalid aspect ratio.")

                        # Call the generate_with_YourDesigner function
                        YourDesigner_image, seed, returned_prompt = generate_with_YourDesigner(
                            YourDesigner_prompt,
                            st.session_state.selected_ratio_api,
                            st.session_state.selected_style,
                            st.session_state.selected_palette
                        )

                        # Store the generated YourDesigner in session state
                        st.session_state.YourDesigner_image = YourDesigner_image
                        st.session_state.seed = seed
                        st.session_state.returned_prompt = returned_prompt

                        st.session_state.modified_image = None  # Reset the modified image

                        # Convert PIL image to bytes for download
                        buffered = BytesIO()
                        YourDesigner_image.save(buffered, format="PNG")
                        image_bytes = buffered.getvalue()

                        if YourDesigner_image:
                            st.success("YourDesigner generated successfully!")
                            st.image(YourDesigner_image, caption="Generated YourDesigner", use_column_width=True)
                            st.download_button(
                                label="Download YourDesigner",
                                data=image_bytes,
                                file_name="YourDesigner.png",
                                mime="image/png"
                            )
                        else:
                            st.error("Could not download the YourDesigner image.")
                    except ValueError as e:
                        st.error(f"Error: {str(e)}")

            # Display the original YourDesigner (always)
            if st.session_state.YourDesigner_image is not None:
                # Add a section for modifying the image
                st.subheader("Modify Your Image")
                
                # Text area to specify modification details
                modification_prompt = st.text_area("Describe the modification you want (e.g., 'increase brightness', 'add a filter'):")

                # The "Modify Image" button is always there
                if st.button("Modify Image"):
                    with st.spinner("Modifying your image..."):
                        try:
                            modification_prompt = modify_prompt(st.session_state.returned_prompt, modification_prompt)

                            # Modify the original image based on the user's input
                            st.session_state.YourDesigner_image, new_seed, returned_prompt = generate_with_YourDesigner(
                                modification_prompt,
                                st.session_state.selected_ratio_api,
                                st.session_state.selected_style,
                                st.session_state.selected_palette,
                                seed=st.session_state.seed
                            )
                            
                            # Convert the modified image to bytes for downloading
                            buffered_modified = BytesIO()
                            st.session_state.YourDesigner_image.save(buffered_modified, format="PNG")
                            modified_image_bytes = buffered_modified.getvalue()

                            # Display the modified image in the same place (overwrites the original display)
                            st.image(st.session_state.YourDesigner_image, caption="Modified YourDesigner", use_column_width=True)
                            
                            # Download button for the modified image
                            st.download_button(
                                label="Download Modified Image",
                                data=modified_image_bytes,
                                file_name="modified_YourDesigner.png",
                                mime="image/png"
                            )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    elif processing_mode == "Batch Processing via CSV":
        st.subheader("Batch Processing via CSV")

        # Instructions to the user
        st.write("Upload a CSV file with a 'prompt' column.")

        # File uploader for CSV
        uploaded_csv = st.file_uploader("Upload CSV file", type=['csv'])

        # Interface for selecting parameters
        # Create columns for layout
        col1, col2, col3 = st.columns([1, 1, 3])

        # Portrait ratios in the first column
        with col1:
            st.markdown('<div class="ratios"><h4>Portrait</h4></div>', unsafe_allow_html=True)
            for label, _ in const.PROTRAIT_RATIOS.items():
                if st.button(label, key=f'batch_portrait_{label}'):
                    update_ratio(label)

        # Landscape ratios in the second column
        with col2:
            st.markdown('<div class="ratios"><h4>Landscape</h4></div>', unsafe_allow_html=True)
            for label, _ in const.LANDSCAPE_RATIOS.items():
                if st.button(label, key=f'batch_landscape_{label}'):
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
        st.session_state.selected_style = st.selectbox("Choose a style:", const.styles, key='batch_style')

        # Add color palette selection with demo
        st.subheader("Select a Color Palette")
        palette_choice = st.radio("Choose a color palette:", const.palettes, key='batch_palette')

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

        if uploaded_csv is not None:
            # Check if the ratio is selected
            if st.session_state.selected_ratio:
                if st.button("Process CSV"):
                    with st.spinner("Processing CSV..."):
                        # Call the batch processing function
                        zip_data,zipfile = process_csv_prompts(
                            uploaded_csv,
                            st.session_state.selected_ratio,
                            st.session_state.selected_style,
                            st.session_state.selected_palette,
                            st.session_state["name"],
                            "Generate With Yourdesigner"
                        )
                        st.download_button(
                                    label="Download ZIP File",
                                    data=zipfile,
                                    file_name="generated_images_and_mapping.zip",
                                    mime="application/zip"
                                )
            else:
                st.warning("Please select an aspect ratio before processing the CSV.")
