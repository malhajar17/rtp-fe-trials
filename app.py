# app.py
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

# Import the ProfileUI class from profile_element.py
from ui_elements.profile_element import ProfileUI

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

    # Create an instance of ProfileUI
    profile_ui = ProfileUI(username)

    # Display the profile picture and username
    profile_ui.display_profile()

    # Display the buttons and handle clicks
    view_history_button, edit_profile_button = profile_ui.display_buttons()
    profile_ui.handle_button_clicks(view_history_button, edit_profile_button)

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
