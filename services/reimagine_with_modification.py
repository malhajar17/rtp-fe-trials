import zipfile
import streamlit as st
import constants as const
from io import BytesIO
from utils.server_utils import reimagine_image, generate_with_YourDesigner, modify_prompt
from utils.batch_processing_utils import process_zip_images  # Import the new function
import pandas as pd

def run():
    st.title("Reimagine with Modification")

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
        st.session_state.YourDesigner_image = None  # Store the reimagined image
    if 'modified_image' not in st.session_state:
        st.session_state.modified_image = None  # Store the modified image
    if 'seed' not in st.session_state:
        st.session_state.seed = 0  # Store the seed for modifications
    if 'returned_prompt' not in st.session_state:
        st.session_state.returned_prompt = ""  # Store the original prompt

    def update_ratio(choice):
        st.session_state.selected_ratio = choice
        ratio = const.PROTRAIT_RATIOS.get(choice) or const.LANDSCAPE_RATIOS.get(choice)
        if ratio:
            if const.PROTRAIT_RATIOS.get(choice):
                st.session_state.width = 200  # Fixed width for portrait
                st.session_state.height = int(200 * (ratio[1] / ratio[0]))  # Adjust height for portrait
            else:
                st.session_state.height = 200  # Fixed height for landscape
                st.session_state.width = int(200 * (ratio[0] / ratio[1]))  # Adjust width for landscape
        else:
            st.write("Ratio not found")  # Debugging statement

    # Add processing mode selection
    processing_mode = st.radio("Select Processing Mode", ["Single Image", "Batch Processing via ZIP"])

    if processing_mode == "Single Image":

        # Check if an image has been uploaded
        uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            img_bytes = uploaded_file.read()

            # Aspect Ratio Controls
            st.subheader("Select Aspect Ratio")
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                st.markdown('<div class="ratios"><h4>Portrait</h4></div>', unsafe_allow_html=True)
                for label, _ in const.PROTRAIT_RATIOS.items():
                    if st.button(label, key=f'portrait_{label}'):
                        update_ratio(label)
            with col2:
                st.markdown('<div class="ratios"><h4>Landscape</h4></div>', unsafe_allow_html=True)
                for label, _ in const.LANDSCAPE_RATIOS.items():
                    if st.button(label, key=f'landscape_{label}'):
                        update_ratio(label)

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

            # Style and Palette selection
            st.subheader("Select a Style")
            st.session_state.selected_style = st.selectbox("Choose a style:", const.styles)

            st.subheader("Select a Color Palette")
            palette_choice = st.radio("Choose a color palette:", const.palettes)
            st.session_state.selected_palette = palette_choice

            st.markdown("### Color Palette Preview")
            colors = const.palette_colors.get(palette_choice, [])
            swatch_html = "".join([
                f"<div style='display:inline-block;width:30px;height:30px;background-color:{color};margin-right:5px;border-radius:4px;'></div>"
                for color in colors
            ])
            st.markdown(swatch_html, unsafe_allow_html=True)

            # Generate Reimagined Image (No prompt required)
            if st.session_state.selected_ratio:
                if st.button("Reimagine Image"):
                    with st.spinner("Reimagining your image..."):
                        try:
                            st.session_state.selected_ratio_api = const.aspect_ratio_mapping.get(st.session_state.selected_ratio)
                            # Ensure the aspect ratio is valid
                            if not st.session_state.selected_ratio_api:
                                st.error("Selected aspect ratio is not supported.")
                                raise ValueError("Invalid aspect ratio.")

                            # Call reimagine_image function
                            reimagined_image, seed, returned_prompt = reimagine_image(
                                img_bytes,
                                st.session_state.selected_ratio_api,
                                st.session_state.selected_style,
                                st.session_state.selected_palette
                            )

                            # Store the reimagined image, seed, and prompt
                            st.session_state.YourDesigner_image = reimagined_image
                            st.session_state.seed = seed
                            st.session_state.returned_prompt = returned_prompt

                            # Convert image to bytes for download
                            buffered = BytesIO()
                            reimagined_image.save(buffered, format="PNG")
                            image_bytes = buffered.getvalue()

                            # Display the reimagined image
                            if reimagined_image:
                                st.success("Image reimagined successfully!")
                                st.image(reimagined_image, caption="Reimagined Image", use_column_width=True)
                                st.download_button(
                                    label="Download Reimagined Image",
                                    data=image_bytes,
                                    file_name="reimagined_image.png",
                                    mime="image/png"
                                )
                            else:
                                st.error("Could not download the reimagined image.")
                        except ValueError as e:
                            st.error(f"Error: {str(e)}")

            # Display the original reimagined image (if it exists)
            if st.session_state.YourDesigner_image is not None:
                st.subheader("Modify Your Image")

                # Text area to specify modification details
                modification_prompt = st.text_area("Describe the modification you want (e.g., 'add more color', 'brighten the image'):")

                if st.button("Modify Image"):
                    with st.spinner("Modifying your image..."):
                        try:
                            # Modify the original prompt with the user's input
                            modification_prompt = modify_prompt(st.session_state.returned_prompt, modification_prompt)

                            # Regenerate the image with the modified prompt
                            st.session_state.YourDesigner_image, new_seed, returned_prompt = generate_with_YourDesigner(
                                modification_prompt,
                                st.session_state.selected_ratio_api,
                                st.session_state.selected_style,
                                st.session_state.selected_palette,
                                seed=st.session_state.seed
                            )

                            # Convert the modified image to bytes for download
                            buffered_modified = BytesIO()
                            st.session_state.YourDesigner_image.save(buffered_modified, format="PNG")
                            modified_image_bytes = buffered_modified.getvalue()

                            # Display the modified image
                            st.image(st.session_state.YourDesigner_image, caption="Modified Image", use_column_width=True)

                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    elif processing_mode == "Batch Processing via ZIP":
            st.subheader("Batch Processing via ZIP")

            # Instructions to the user
            st.write("Upload a ZIP file containing images.")

            # File uploader for ZIP
            uploaded_zip = st.file_uploader("Upload ZIP file", type=['zip'])

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
            st.session_state.selected_palette = palette_choice

            # Display color swatches for the selected palette
            st.markdown("### Color Palette Preview")
            colors = const.palette_colors.get(palette_choice, [])
            swatch_html = "".join([
                f"<div style='display:inline-block;width:30px;height:30px;background-color:{color};margin-right:5px;border-radius:4px;'></div>"
                for color in colors
            ])
            st.markdown(swatch_html, unsafe_allow_html=True)

            if uploaded_zip is not None:
                # Check if the ratio is selected
                if st.session_state.selected_ratio:
                    if st.button("Process ZIP"):
                        with st.spinner("Processing ZIP file..."):
                            try:
                                # Call the batch processing function
                                images_and_mapping = process_zip_images(
                                    uploaded_zip,
                                    st.session_state.selected_ratio,
                                    st.session_state.selected_style,
                                    st.session_state.selected_palette,
                                    st.session_state.get("name", ""),
                                    "Reimagine With Modification"
                                )
                                if images_and_mapping is not None:
                                    # Store images and mapping in session state
                                    st.session_state['batch_images'] = images_and_mapping['images']
                                    st.session_state['mapping'] = images_and_mapping['mapping']

                                    st.success("Batch processing completed. You can now view and modify images.")

                                    # Display images in a gallery
                                    display_image_gallery()

                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    else:
                        # If images are already processed, display the gallery
                        if 'batch_images' in st.session_state:
                            display_image_gallery()
                else:
                    st.warning("Please select an aspect ratio before processing the ZIP.")

            # Download button for modified images
            if 'batch_images' in st.session_state:
                    zip_data = create_zip_from_session()
                    if zip_data is not None:
                        st.download_button(
                            label="Download Reimagined Images",
                            data=zip_data,
                            file_name="reimagined_images_and_mapping.zip",
                            mime="application/zip"
                        )

def display_image_gallery():
        images = st.session_state['batch_images']
        mapping = st.session_state['mapping']

        st.subheader("Image Gallery (Click on an image to modify)")

        # Determine the number of columns (adjust as needed)
        cols = st.columns(4)

        for idx, (img_name, img_data) in enumerate(images.items()):
            col = cols[idx % 4]
            with col:
                # Display the image with a button
                if st.button("Modify this Image", key=f"img_btn_{idx}"):
                    open_image_dialog(img_name)
                st.image(img_data, use_column_width=True, caption=img_name)

@st.dialog("Modify image")
def open_image_dialog(img_name):
        images = st.session_state['batch_images']
        mapping = st.session_state['mapping']

        # Simulate a dialog using an expander (since st.dialog might not be available)
        with st.expander(f"Modify Image: {img_name}", expanded=True):
            st.image(images[img_name], use_column_width=True)
            st.write("Enter a modification prompt:")
            modification_prompt = st.text_area("Modification Prompt", key=f"mod_prompt_{img_name}")

            if st.button("Apply Modification", key=f"apply_mod_{img_name}"):
                with st.spinner("Modifying image..."):
                    try:
                        # Get the original prompt from mapping
                        original_prompt = mapping[img_name]['prompt']
                        selected_ratio_api = const.aspect_ratio_mapping.get(st.session_state.selected_ratio)

                        # Modify the prompt
                        new_prompt = modify_prompt(original_prompt, modification_prompt)

                        # Regenerate the image
                        modified_image, new_seed, returned_prompt = generate_with_YourDesigner(
                            new_prompt,
                            selected_ratio_api,
                            st.session_state.selected_style,
                            st.session_state.selected_palette,
                            seed=mapping[img_name]['seed']
                        )

                        # Update the image and mapping in session state
                        images[img_name] = modified_image
                        mapping[img_name]['seed'] = new_seed
                        mapping[img_name]['prompt'] = returned_prompt

                        st.success("Image modified successfully.")
                        st.image(modified_image, use_column_width=True, caption="Modified Image")

                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def create_zip_from_session():
        images = st.session_state['batch_images']
        mapping = st.session_state['mapping']

        if not images:
            st.error("No images to download.")
            return None

        # Create a zip file in memory
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            # Add images to zip
            for img_name, img_data in images.items():
                # Convert image to bytes
                img_byte_arr = BytesIO()
                img_data.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()

                zipf.writestr(img_name, img_bytes)

            # Add mapping CSV
            mapping_df = pd.DataFrame.from_dict(mapping, orient='index')
            mapping_csv = mapping_df.to_csv(index=False)
            zipf.writestr("mapping.csv", mapping_csv)

        output_zip.seek(0)
        zip_data = output_zip.getvalue()
        return zip_data