import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import streamlit_authenticator as stauth
import yaml
import streamlit as st
from pathlib import Path

def load_credentials(config_path="config.yaml"):
    # Load the authentication config from a YAML file
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def create_authenticator(credentials):
    # Create an authenticator object using credentials
    authenticator = stauth.Authenticate(
        credentials["credentials"],
        credentials["cookie"]["name"],
        credentials["cookie"]["key"],
        credentials["cookie"]["expiry_days"],
    )
    return authenticator

def login(authenticator):
    # Perform login operation
    authenticator.login()
    return st.session_state["authentication_status"], st.session_state["name"]

def logout(authenticator):
    # Perform logout operation
    authenticator.logout("Logout", "sidebar")

# Helper function to save credentials
def save_credentials(credentials, config_path="config.yaml"):
    try:
        with open(config_path, 'w') as file:
            yaml.dump(credentials, file, default_flow_style=False)
        st.success("Credentials saved successfully!")
    except Exception as e:
        st.error(f"Error saving credentials: {str(e)}")

# Sign-up dialog definition
@st.dialog("Create a New Account")
def sign_up(authenticator, credentials):
    st.write("Fill in the details below to create your account.")

    # Input fields for the sign-up form
    new_username = st.text_input("Username", help="Choose a unique username")
    new_email = st.text_input("Email", help="Enter a valid email address")
    new_name = st.text_input("Full Name", help="Enter your full name")
    new_password = st.text_input("Password", type="password", help="Choose a strong password")

    st.write("Make sure to double-check your details before submitting.")

    # Process form submission when 'Submit' is clicked
    if st.button("Submit"):
        # Validate if username or email already exists
        if new_username in credentials["credentials"]["usernames"]:
            st.error("Sorry, this username is already taken. Please choose a different one.")
        elif any(user["email"] == new_email for user in credentials["credentials"]["usernames"].values()):
            st.error("This email is already registered. Please use another email or log in.")
        else:
            # Hash the password for security
            hashed_password = new_password

            # Update the credentials
            credentials["credentials"]["usernames"][new_username] = {
                "name": new_name,
                "email": new_email,
                "password": hashed_password
            }

            # Save the updated credentials
            save_credentials(credentials, config_path="config.yaml")

            # Automatically log in the user after successful sign-up
            st.session_state["authentication_status"] = True
            st.session_state["name"] = new_name
            st.session_state["username"] = new_username
            st.session_state["password"] = new_password

            # Simulate login
            authenticator.login()

            st.success(f"Welcome {new_name}! You are now logged in.")
            st.rerun()

def check_signup():
    # Display sign-up option
    if st.button("Sign Up", key="check_signup_button"):  # Adding a unique key here as well
        return True
    return False
