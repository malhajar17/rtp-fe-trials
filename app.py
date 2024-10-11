import streamlit as st
import os
import base64
from PIL import Image
from io import BytesIO

import constants as const
from utils import auth_utils as auth

# Import services
from services import (
    upscale_image,
    resize_with_bleed,
    remove_background,
    generate_flyer,
    generate_with_yourdesigner,
    describe_image,
    remix_image,
    reimagine_with_modification,
)

# Streamlit page configuration
st.set_page_config(
    page_title="PrintOclock's YourDesigner",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for UI improvements
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("styles.css")

# Load credentials from config file
credentials = auth.load_credentials()
st.session_state["credentials"] = credentials
authenticator = auth.create_authenticator(credentials)

# Check if authentication_status is already in session state
if 'authentication_status' not in st.session_state:
    st.session_state["authentication_status"] = None

# Check authentication status
authentication_status = st.session_state["authentication_status"]
name = st.session_state.get("name", "")

# Handle the authentication flow
if authentication_status != True:  # Only show login/sign-up if not authenticated
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 class="project-title">PrintOclock's YourDesigner</h1>
            <h3 class="project-motto">Design Smartly</h3>
        </div>
    """, unsafe_allow_html=True)

    # Check if the user is already authenticated
    authentication_status, name = auth.login(authenticator)

    if authentication_status:
        # Set session state after successful login
        st.session_state["authentication_status"] = True
        st.session_state["name"] = name
        st.rerun()  # Reload the app to show the authenticated screen

    # If not authenticated, show the sign-up button
    if not authentication_status and auth.check_signup():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        auth.sign_up(authenticator, credentials)  # Sign-up form
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Once logged in, display the rest of the app
    st.session_state['username'] = name
    username = name

    # Load or set a default profile picture
    profile_pic_path = f"profile_pics/{username}.png"
    if os.path.exists(profile_pic_path):
        profile_pic = Image.open(profile_pic_path)
    else:
        profile_pic = Image.open("default_profile_pic.png")

    # Convert profile picture to base64
    buffered = BytesIO()
    profile_pic.save(buffered, format="PNG")
    profile_pic_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Display profile picture and username
    st.sidebar.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{profile_pic_base64}" width="80" style="border-radius: 50%;">
            <h3 style="margin-bottom: 0;">{username}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Create buttons using Streamlit's button widgets
    with st.sidebar:
        st.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            view_history_button = st.button("View History")
        with col2:
            edit_profile_button = st.button("Edit Profile")
        st.markdown('</div>', unsafe_allow_html=True)

    # Handle button clicks
    if view_history_button:
        # Your code to display user history goes here
        st.write(f"Displaying {username}'s history.")
    if edit_profile_button:
        # Your code to edit the profile goes here
        st.write(f"Editing {username}'s profile.")

    # Sidebar for user inputs
    st.sidebar.title("Image Processing Controls")

    # Select service: Upscale or Resize with Bleed
    service_choice = st.sidebar.radio("Choose a service", [
        "Upscale Image", "Resize with Bleed", "Remove Background", 
        "Generate Flyer", "Generate with YourDesigner", 
        "Describe Image with YourDesigner", "Remix Image", "Reimagine with Modification"
    ])

    # Now call the appropriate service
    if service_choice == "Upscale Image":
        upscale_image.run()
    elif service_choice == "Resize with Bleed":
        resize_with_bleed.run()
    elif service_choice == "Remove Background":
        remove_background.run()
    elif service_choice == "Generate Flyer":
        generate_flyer.run()
    elif service_choice == "Generate with YourDesigner":
        generate_with_yourdesigner.run()
    elif service_choice == "Describe Image with YourDesigner":
        describe_image.run()
    elif service_choice == "Remix Image":
        remix_image.run()
    elif service_choice == "Reimagine with Modification":
        reimagine_with_modification.run()

    # Place the logout button at the bottom
    with st.sidebar:
        auth.logout(authenticator)

# Handle incorrect login
if authentication_status == False:
    st.error("Username or password is incorrect.")
