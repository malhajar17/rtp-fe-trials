import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


st.set_page_config(layout='wide')


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

spacer_left, form, spacer_right = st.columns([1, 0.8, 1])
with form:
    authenticator.login(location='main')

if st.session_state["authentication_status"]:
    with form:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')

    st.title('Some content')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')