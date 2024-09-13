import streamlit as st
import pyotp
import qrcode
from io import BytesIO
from base64 import b64encode, b64decode
from PIL import Image

# Simulating a user database (stored in memory for simplicity)
user_secrets = {}

def generate_user_identifier(user_key):
    # Use the user_key as a unique identifier for the user
    return f"{user_key}"

def enroll_user(user_key):
    # Generate a unique identifier for the user
    user_id = generate_user_identifier(user_key)

    # Generate a unique secret for the user (if not already enrolled)
    if user_id not in user_secrets:
        secret = pyotp.random_base32()
        user_secrets[user_id] = secret
    else:
        secret = user_secrets[user_id]

    totp = pyotp.TOTP(secret)

    # Generate provisioning URL for Google Authenticator or similar apps
    provisioning_url = totp.provisioning_uri(name=secret, issuer_name='BroxelAuth')

    # Generate QR code as base64 image
    qr_img = qrcode.make(provisioning_url)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    qr_img_b64 = b64encode(buf.getvalue()).decode('utf-8')

    return provisioning_url, qr_img_b64, secret

def validate_otp(secret, user_input_otp):
    # Validate the OTP using the stored secret
    totp = pyotp.TOTP(secret)
    return totp.verify(user_input_otp)

# Streamlit UI
st.title("Authenticator App Enrollment Example")
st.text("Using TOTP (Time-based One-Time Password Algorithm) - RFC 6238")

# Initialize session state for secret if it doesn't exist
if 'secret' not in st.session_state:
    st.session_state['secret'] = None

# User Key input for enrollment
with st.form(key='enrollment_form'):
    user_key_input = st.text_input("Enter an email (testing purposes as UserId)", max_chars=50)
    submit_enroll = st.form_submit_button("Enroll")

if submit_enroll and user_key_input:
    # Enroll the user and store the secret in session state
    provisioning_url, qr_img_b64, secret = enroll_user(user_key_input)
    st.session_state['secret'] = secret  # Persist the secret key in session state

    st.write(f"User Secret: {secret}")
    st.write(f"User Key: {user_key_input}")
    st.write(f"Provisioning URL: [Scan with your authenticator app]({provisioning_url})")

    # Display QR code
    qr_img = Image.open(BytesIO(b64decode(qr_img_b64)))
    st.image(qr_img, caption="Scan this QR code with Google or Microsoft Authenticator")

# OTP Verification input
st.subheader("Verify OTP")
with st.form(key='verification_form'):
    otp_input = st.text_input("Enter the OTP from your authenticator app", max_chars=6)
    submit_verify = st.form_submit_button("Verify OTP")

# Validate the OTP if the user has enrolled and submitted the OTP
if submit_verify and otp_input and st.session_state['secret']:
    is_valid = validate_otp(st.session_state['secret'], otp_input)
    if is_valid:
        st.success("OTP is valid!")
    else:
        st.error("OTP is invalid!")
