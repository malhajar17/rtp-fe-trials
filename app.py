import streamlit as st
from server_utils import *
import elements as ui
import constants as const  # Import your constants
from io import BytesIO
import utils  # Import the utils module
import image_calc_utils as img_utils

# Streamlit page configuration
st.set_page_config(
    page_title="Image Processing App",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the custom CSS file
load_css(const.STYLE_FILE)

# Sidebar for user inputs
st.sidebar.title("Image Processing Controls")
uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

# Select service: Upscale or Resize with Bleed
service_choice = st.sidebar.radio("Choose a service", ["Upscale Image", "Resize with Bleed", "Remove Background", "Generate Flyer","Generate with YourDesigner","Describe Image with YourDesigner","Remix Image"])

if service_choice == "Upscale Image":
    upscale_factor = st.sidebar.slider("Upscale Factor", const.MIN_UPSCALE_FACTOR, const.MAX_UPSCALE_FACTOR, const.DEFAULT_UPSCALE_FACTOR)
    st.sidebar.info("Use the slider to select how much you want to upscale your image.")

    st.title("Image Upscaler")
    st.subheader("Upload an image and choose an upscale factor. The app will enhance your image and provide a download link.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)

        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Upscaling your image..."):
                try:
                    upscaled_image, s3_key = upscale_image(const.UPSCALE_SERVICE_URL, img_bytes, upscale_factor)

                    # Convert PIL image to bytes
                    buffered = BytesIO()
                    upscaled_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    if upscaled_image:
                        st.success("Image upscaled successfully!")
                        st.image(upscaled_image, caption="Upscaled Image", use_column_width=True)
                        st.download_button(
                            label="Download Upscaled Image",
                            data=image_bytes,
                            file_name=s3_key.split("/")[-1],
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")

elif service_choice == "Resize with Bleed":
    resize_type = st.sidebar.radio("Resize Type", ["Custom Dimensions", "Standard Resize"])

    if resize_type == "Custom Dimensions":
        st.title("Image Resize with Custom Dimensions")
        st.subheader("Upload an image and specify the base dimensions. The app will resize your image accordingly.")

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()  # Read the file only once and reuse the bytes

            initial_width_mm, initial_height_mm, initial_width_px, initial_height_px = img_utils.get_initial_dimensions(img_bytes)

            # Base dimensions input by user
            base_width_mm = st.sidebar.number_input("Base Width (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_width_mm), step=1.0)
            base_height_mm = st.sidebar.number_input("Base Height (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_height_mm), step=1.0)

            # Move resize_option here so it's chosen before processing
            resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Scale Down and Fill Bleed", "Crop Image"])

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, base_width_mm, base_height_mm, resize_option)

    elif resize_type == "Standard Resize":
        st.title("Standard Image Resize")
        st.subheader("Upload an image and choose a standard format. The app will resize your image to match the selected format and add the bleed.")

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()  # Read the file only once and reuse the bytes

            # Get initial dimensions in both mm and pixels
            initial_width_mm, initial_height_mm, initial_width_px, initial_height_px = img_utils.get_initial_dimensions(img_bytes)
            # Select orientation first
            orientation = st.sidebar.radio("Choose orientation", ["Portrait", "Paysage"])

            # Determine the list of available formats based on the orientation
            available_formats = [f for f in const.FORMATS.keys() if orientation.lower() in f]

            # Select format based on the chosen orientation
            format_choice = st.sidebar.selectbox("Choose a format", available_formats)

            # Get dimensions and bleed based on the selected format
            dimensions, bleed_dimensions = const.FORMATS.get(format_choice)
            format_width_mm = dimensions[0]
            format_height_mm = dimensions[1]

            # Convert format dimensions to pixels at 300 DPI
            format_width_px = int((format_width_mm / 25.4) * 300)
            format_height_px = int((format_height_mm / 25.4) * 300)

            # Check if image is larger than the specified dimensions
            if initial_width_px > format_width_px or initial_height_px > format_height_px:
                resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Scale Down and Fill Bleed", "Crop Image"])
            else:
                resize_option = None  # No need to choose, image will just be resized

            st.sidebar.info(f"Selected Format: {format_choice}")
            st.sidebar.info(f"Base dimensions: {int(initial_width_mm)} mm x {int(initial_height_mm)} mm")
            st.sidebar.info(f"Final dimensions with Bleed mm: {format_width_mm} mm x {format_height_mm} mm")

            

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, format_width_px, format_height_px, resize_option)


elif service_choice == "Remove Background":
    st.title("Background Remover")
    st.subheader("Upload an image, and the app will remove its background.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)

        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Removing the background..."):
                try:
                    bg_removed_image, image_bytes = remove_background(img_bytes)
                    buffered = BytesIO()
                    bg_removed_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    # Create checkerboard background
                    width, height = bg_removed_image.size
                    checkerboard = ui.create_checkerboard(width, height)

                    # Overlay the image onto the checkerboard
                    checkerboard.paste(bg_removed_image, (0, 0), bg_removed_image)

                    st.success("Background removed successfully!")
                    st.image(checkerboard, caption="Background Removed Image", use_column_width=True)
                    st.download_button(
                        label="Download Image with Background Removed",
                        data=image_bytes,
                        file_name="bg_removed_image.png",
                        mime="image/png"
                    )
                except ValueError as e:
                    st.error(f"Error: {str(e)}")

elif service_choice == "Generate Flyer":
    st.title("Flyer Generator")
    st.subheader("Enter the details to generate your flyer image.")

    # Text field for flyer content
    flyer_text = st.text_area("Enter the flyer text here:", "Your flyer content goes here.")
    
    # Text field for flyer design
    flyer_design = st.text_area("Enter the flyer design instructions here:", "E.g., vibrant colors, modern style, minimalistic design, etc.")

    if flyer_text and flyer_design:
        if st.sidebar.button("Generate Flyer"):
            with st.spinner("Generating your flyer..."):
                try:
                    # Combine the text and design instructions into one prompt
                    flyer_prompt = f"Design a flyer with the following text: '{flyer_text}'. Design instructions: {flyer_design}."

                    flyer_image, s3_key = generate_flyer_image(flyer_prompt)

                    # Convert PIL image to bytes
                    buffered = BytesIO()
                    flyer_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    if flyer_image:
                        st.success("Flyer generated successfully!")
                        st.image(flyer_image, caption="Generated Flyer", use_column_width=True)
                        st.download_button(
                            label="Download Flyer",
                            data=image_bytes,
                            file_name=s3_key.split("/")[-1],
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the flyer image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")

elif service_choice == "Generate with YourDesigner":

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
        st.session_state.seed = 0  # Store the modified image
    if 'returned_prompt' not in st.session_state:
        st.session_state.returned_prompt = ""  # Store the modified image

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
                    print(st.session_state.seed)

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
                    print(st.session_state.seed)

                    try:
                        modification_prompt = modify_prompt(st.session_state.returned_prompt,modification_prompt)
                        print(modification_prompt)
                        # Modify the original image based on the user's input
                        st.session_state.YourDesigner_image,new_seed,returned_prompt =generate_with_YourDesigner(
                        modification_prompt,
                        st.session_state.selected_ratio_api,
                        st.session_state.selected_style,
                        st.session_state.selected_palette,
                        seed=st.session_state.seed)
                        
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

elif service_choice == "Describe Image with YourDesigner":
    st.title("Image Description")
    st.subheader("Upload an image, and the app will generate a description for the image.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        img_bytes = uploaded_file.read()

        if st.sidebar.button("Generate Description"):
            with st.spinner("Generating description..."):
                try:
                    # Call a function or API that returns a description for the image
                    description = describe_image(img_bytes)  
                    st.success("Description generated successfully!")
                    st.write(f"**Description:** {description}")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")


elif service_choice == "Remix Image":

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
