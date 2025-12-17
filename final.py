import streamlit as st
from streamlit import session_state as ss
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import time
import io

# --- Custom Modules ---
# Ensure 'calcfunctions.py' is in the same folder in your GitHub repo
try:
    from calcfunctions import compute_figure
except ImportError:
    # Fallback for testing if file is missing
    st.error("calcfunctions module not found. Please ensure it is in the repository.")
    def compute_figure(*args):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])
        return fig, ax

# --- Initialization ---
def resetfunc():
    ss.hpts1m2 = 14.0
    ss.hpts2m2 = 27.0
    ss.v2g_mon15 = 142.0
    ss.v2g_mon5 = 6.0
    ss.sc_mon15 = 100.5
    ss.sc_mon5 = 4.0
    ss.paper = True
    ss.fig = None
    ss.ax = None
    # We add a buffer to session state to hold the image data
    ss.img_buffer = None 

if "resultsdisplaystate" not in ss:
    ss.resultsdisplaystate = False
    resetfunc()

# --- Email Logic ---
def send_email(recipient_email, fig):
    # Retrieve credentials from Streamlit Secrets
    # On Streamlit Cloud, set these up in your App Settings -> Secrets
    try:
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]

    except Exception:
        st.error("Email secrets not found. Please configure .streamlit/secrets.toml")
        return

    if not recipient_email:
        st.warning("Please enter an email address first.")
        return

    subject = "Your LCODR Results"
    body = (
        "Dear IAEE Conference Attendee,\n\n"
        "Thank you very much for showing an interest in our LCODR framework. "
        "The attached picture shows how your demand flexibility compares against "
        "the most cost-competitive energy storage solution. If you are interested "
        "in the LCODR framework, read our preprint: https://arxiv.org/abs/2502.03124 \n\n"
        "Kind regards,\nJacob Thrän"
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Save figure to memory (Buffer) for attachment
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Create the Image Attachment
    image = MIMEImage(buf.read())
    image.add_header('Content-Disposition', 'attachment; filename="LCODR_results.png"')
    msg.attach(image)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        st.success(f"Email sent successfully to {recipient_email}!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# --- Data Saving Logic ---
def save_data_cloud():
    # NOTE: You cannot save to local CSV files on Streamlit Cloud (the filesystem is ephemeral).
    # To save data, you must connect to Google Sheets, AWS S3, or a database.
    # For now, we will just print what would be saved.
    
    data = {
        "V2G10h": [ss.v2g_mon5], 
        "V2G15h": [ss.v2g_mon15], 
        "SC10h": [ss.sc_mon5], 
        "SC15h": [ss.sc_mon15], 
        "HPTS1m2": [ss.hpts1m2], 
        "HPTS2m2": [ss.hpts2m2], 
        "TimestampX": [time.time()]
    }
    # In a real deployment, write this 'data' to your cloud database here.
    # st.write("Data captured (not saved to disk in this demo):", data)

def change():
    ss.resultsdisplaystate = False
    resetfunc()

# --- Streamlit UI ---
st.title("Find your personal Levelised Cost of Demand Response (LCODR)")

st.subheader("Smart Charging")
st.write("*In a Smart Charging scheme, you allow a third party...*")
ss.sc_mon5 = st.slider("Payment for Smart Charging (10h/day)", 0.0, 300.0, value=ss.sc_mon5, step=1.0, key="sc_mon5_slider")
ss.sc_mon15 = st.slider("Payment for Smart Charging (15h/day)", 0.0, 300.0, value=ss.sc_mon15, step=1.0, key="sc_mon15_slider")

st.subheader("Vehicle-to-Grid")
st.write("*Vehicle-to-Grid schemes work much in the same way...*")
ss.v2g_mon5 = st.slider("Payment for V2G (10h/day)", 0.0, 300.0, value=ss.v2g_mon5, step=1.0, key="v2g_mon5_slider")
ss.v2g_mon15 = st.slider("Payment for V2G (15h/day)", 0.0, 300.0, value=ss.v2g_mon15, step=1.0, key="v2g_mon15_slider")

st.subheader("Heat Pump with Thermal Storage")
st.write("*In this scheme, you will have a thermal storage tank...*")
ss.hpts1m2 = st.slider("Payment for Tank (1 sqm)", 0.0, 300.0, value=ss.hpts1m2, step=1.0, key="hpts1m2_slider")
ss.hpts2m2 = st.slider("Payment for Tank (2 sqm)", 0.0, 300.0, value=ss.hpts2m2, step=1.0, key="hpts2m2_slider")

include_min = st.checkbox("Include minimum participation terms?", value=ss.paper, key="paper_check")

# --- Logic Flow ---

if st.button("Compute"):
    save_data_cloud()
    ss.resultsdisplaystate = True
    
    # Generate the figure
    # Note: We pass the 'include_min' value directly
    ss.fig, ss.ax = compute_figure(
        ss.v2g_mon5, ss.v2g_mon15,
        ss.sc_mon5, ss.sc_mon15,
        1000, ss.hpts1m2, ss.hpts2m2, 
        "Your LCODR Results", include_min
    )

if ss.resultsdisplaystate and ss.fig is not None:
    # 1. Display the plot directly from the figure object (No file needed)
    st.pyplot(ss.fig)

    # 2. Email Section
    st.write("---")
    email_input = st.text_input("Enter your email to receive the results:")
    
    if st.button("Send Email"):
        send_email(email_input, ss.fig)

    st.write("---")
    if st.button("Restart"):
        change()
        st.experimental_rerun()
