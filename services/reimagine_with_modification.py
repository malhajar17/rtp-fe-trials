# services/reimagine_with_modification.py
import streamlit as st
import constants as const
from io import BytesIO
from utils.server_utils import reimagine_image, generate_with_YourDesigner, modify_prompt

def run():
    st.title("Reimagine with Modification")

    # Initialize session state variables similar to Generate with YourDesigner
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
                        print(st.session_state.selected_ratio_api)
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

                        # Download button for the modified image
                        st.download_button(
                            label="Download Modified Image",
                            data=modified_image_bytes,
                            file_name="modified_image.png",
                            mime="image/png"
                        )

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
