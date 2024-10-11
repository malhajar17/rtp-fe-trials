# ui_elements/profile_element.py
import streamlit as st
import os
import base64
from PIL import Image
from io import BytesIO
import boto3
from datetime import datetime
from utils.auth_utils import save_credentials

class ProfileUI:
    def __init__(self, username):
        self.username = username
        self.profile_pic_base64 = self.get_profile_pic_base64()
        self.s3_client = self.create_s3_client()

    def get_profile_pic_base64(self):
        # Load or set a default profile picture
        profile_pic_path = f"profile_pics/{self.username}.png"
        if os.path.exists(profile_pic_path):
            profile_pic = Image.open(profile_pic_path)
        else:
            profile_pic = Image.open("default_profile_pic.png")

        # Convert profile picture to base64
        buffered = BytesIO()
        profile_pic.save(buffered, format="PNG")
        profile_pic_base64 = base64.b64encode(buffered.getvalue()).decode()
        return profile_pic_base64

    def display_profile(self):
        # Display profile picture and username
        st.sidebar.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{self.profile_pic_base64}" width="80" style="border-radius: 50%;">
                <h3 style="margin-bottom: 0;">{self.username}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    def display_buttons(self):
        # Create buttons using Streamlit's button widgets
        with st.sidebar:
            st.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                view_history_button = st.button("View History")
            with col2:
                edit_profile_button = st.button("Edit Profile")
            st.markdown('</div>', unsafe_allow_html=True)
        return view_history_button, edit_profile_button

    def handle_button_clicks(self, view_history_button, edit_profile_button):
        if view_history_button:
            # View History functionality
            self.view_history()
        if edit_profile_button:
            # Edit Profile functionality
            self.edit_profile()

    def create_s3_client(self):
        # Create an S3 client
        session = boto3.Session(
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets.get("aws_region", "us-east-1")
        )
        s3_client = session.client('s3')
        return s3_client
    
    @st.dialog("Your History")
    def view_history(self):
        # View History functionality
        bucket_name = st.secrets["S3_BUCKET_NAME"]
        user_folder = f"users/{self.username}/"

        # List objects in the user's folder
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=user_folder)
        files = response.get('Contents', [])

        if not files:
            st.info("No files found in your history.")
            return

        # Prepare data for display
        file_data = []
        for file in files:
            key = file['Key']
            if key.endswith('/'):
                continue  # Skip folders
            filename = os.path.basename(key)
            # Extract service and timestamp from filename
            # Assuming filename format: ServiceName_YYYYMMDDHHMMSS.ext
            name_parts = filename.rsplit('.', 1)[0].split('_')
            if len(name_parts) >= 2:
                service_name = name_parts[0]
                timestamp_str = name_parts[1]
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                    timestamp_formatted = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp_formatted = "Unknown"
            else:
                service_name = "Unknown"
                timestamp_formatted = "Unknown"

            file_data.append({
                'filename': filename,
                'service_name': service_name,
                'timestamp': timestamp_formatted,
                'key': key
            })

        for file_info in file_data:
            st.write(f"**Service:** {file_info['service_name']}")
            st.write(f"**Time:** {file_info['timestamp']}")
            # Generate a presigned URL for the file
            url = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name, 'Key': file_info['key']},
                                                        ExpiresIn=3600)
            # Create a download link
            download_link = f'<a href="{url}" download="{file_info["filename"]}">Download {file_info["filename"]}</a>'
            st.markdown(download_link, unsafe_allow_html=True)
            st.markdown("---")

    @st.dialog("Edit Profile")
    def edit_profile(self):
        # Edit Profile functionality
        st.markdown("## Edit Profile")

        # Load the credentials
        credentials = st.session_state["credentials"]
        user_info = credentials["credentials"]["usernames"].get(self.username, {})

        # Input fields for editing the profile
        new_username = st.text_input("Username", value=self.username, help="Enter your username")
        new_name = st.text_input("Full Name", value=user_info.get("name", ""), help="Enter your full name")
        new_email = st.text_input("Email", value=user_info.get("email", ""), help="Enter a valid email address")
        new_password = st.text_input("Password", type="password", help="Enter a new password if you wish to change it")

        # Profile picture upload
        st.markdown("### Update Profile Picture")
        uploaded_file = st.file_uploader("Choose a new profile picture", type=['png', 'jpg', 'jpeg'])

        if st.button("Update Profile"):
            # Validate new username if changed
            if new_username != self.username and new_username in credentials["credentials"]["usernames"]:
                st.error("This username is already taken. Please choose a different one.")
                return

            # Update user info
            if new_username != self.username:
                # Update username in credentials
                credentials["credentials"]["usernames"][new_username] = credentials["credentials"]["usernames"].pop(self.username)
                self.username = new_username
                st.session_state['username'] = new_username

            if new_name:
                credentials["credentials"]["usernames"][self.username]["name"] = new_name
            if new_email:
                credentials["credentials"]["usernames"][self.username]["email"] = new_email
            if new_password:
                # Hash the password for security
                hashed_password = new_password  # Implement proper hashing in production
                credentials["credentials"]["usernames"][self.username]["password"] = hashed_password

            # Save the updated credentials
            save_credentials(credentials, config_path="config.yaml")

            # Update profile picture if uploaded
            if uploaded_file is not None:
                # Save the uploaded file
                image = Image.open(uploaded_file)
                profile_pic_path = f"profile_pics/{self.username}.png"
                image.save(profile_pic_path)
                # Update the profile picture in the session
                self.profile_pic_base64 = self.get_profile_pic_base64()

            st.success("Profile updated successfully.")
            st.rerun()
