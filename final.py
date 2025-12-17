import streamlit as st
from streamlit import session_state as ss
#st.write("hellow world")

import pandas as pd

#import streamlit as st
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
#from email import Encoders

import time
import io

#my own functions
from calcfunctions import compute_figure

def resetfunc():
     ss.hpts1m2 = 14
     ss.hpts2m2 = 27
     ss.v2g_mon15 = 142
     ss.v2g_mon5 = 6
     ss.sc_mon15 = 100.5
     ss.sc_mon5 = 4
     ss.paper = True
     ss.fig = None
     ss.ax = None
     pass

if "resultsdisplaystate" not in ss:
    ss.resultsdisplaystate = False
    resetfunc()

# Define the compute_results function
#def compute_results(a, b, c):
    # Example computation (replace with actual logic)
#    x = a + b + c
#    y = a * b * c
#    z = (a + b) / c if c != 0 else 0
#    return x, y, z

def send_email(email, fig):
    sender_email = st.secrets["sender_email"]
    sender_password = st.secrets["sender_password"]
    recipient_email = email

    if type(email) == 'NoneType':
        st.write("Enter an email-address first (and press ENTER)")
        return

    else:
        subject = "Your LCODR Results"
        body = "Dear IAEE Conference Attendee,\n\nThank you very much for showing an interest in our LCODR framework. The attached picture shows how your demand flexibility compares against the most cost-competitive energy storage solution. If you are interested in the LCODR framework, read our preprint: https://arxiv.org/abs/2502.03124 \n\nKind regards,\nJacob Thrän"

    #with open(ImgFileName, 'rb') as f:
    #    img_data = f.read()

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # 4. Save figure to memory (Buffer)
        buf = io.BytesIO()

        if isinstance(ss.fig, tuple):
            figure_to_send = ss.fig[0]
        else:
            figure_to_send = ss.fig

        figure_to_send.savefig(buf, format='png')
        buf.seek(0)

        # 5. Create the Image Attachment
        image = MIMEImage(buf.read())
        # This header tells the email client to treat it as a file attachment
        image.add_header('Content-Disposition', 'attachment; filename="results_plot.png"')
        msg.attach(image)

        # Attach the image
        #image_path = "C:/Users/simon/local python/Your LCODR results.png"  # Update the path to your PNG file
        #with open(image_path, 'rb') as img_file:
        #    img = MIMEImage(img_file.read())
        #    img.add_header('Content-Disposition', 'attachment', filename="image.png")
        #    msg.attach(img)

    #text = MIMEText("test")
    #msg.attach(text)
    #image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    #msg.attach(image)

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            st.success("Email sent successfully!")
        except smtplib.SMTPAuthenticationError:
            st.error("Failed to login to the SMTP server. Check your email and password.")
        except smtplib.SMTPConnectError:
            st.error("Failed to connect to the SMTP server. Check the server address and port.")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

# Streamlit app
st.title("Find your personal Levelised Cost of Demand Response (LCODR)")

# Input fields for a, b, and c

st.subheader("Smart Charging")
st.write("*In a Smart Charging scheme, you allow a third party (e.g. your energy supplier) to start and stop your EV's charging process. You can always indicate times at which you need your vehicle to be fully charged. Your smart charging contract specifies an average daily plug-in time which your EV must maintain.*")
sc_mon5 = st.slider("How much (in US$) would you expect to be paid monthly to participate with your EV in a smart charging scheme that requires you to be plugged-in at home for an average of **10h/day**?", min_value=0, max_value=300, key="sc_mon5")
sc_mon15 = st.slider("How much (in US$) would you expect to be paid monthly to participate with your EV in a smart charging scheme that requires you to be plugged-in at home for an average of **15h/day**?", min_value=0, max_value=300, key="sc_mon15")

st.subheader("Vehicle-to-Grid")
st.write("*Vehicle-to-Grid schemes work much in the same way to Smart Charging except that the third party can also discharge from your EV's battery to the grid. They must maintain your battery charge level above **33%**. Your V2G contract also specifies an average daily plug-in time which your EV must maintain.*")
v2g_mon5 = st.slider("How much (in US$) would you expect to be paid monthly to participate with your EV in a vehicle-to-grid scheme that requires you to be plugged-in at home for an average of **10h/day**?", min_value=0, max_value=300, key="v2g_mon5")
v2g_mon15 = st.slider("How much (in US$) would you expect to be paid monthly to participate with your EV in a smart charging scheme that requires you to be plugged-in at home for an average of **15h/day**?", min_value=0, max_value=300, key="v2g_mon15")

#st.subheader("Smart Heat Pumps")

#a = st.slider("Monthly remuneration for maximum temperature divergence of 1:", min_value=0, max_value=300, key="a")

#col3, col4 = st.columns(2)
#with col3:
#    v2g_mon5 = st.slider("Monthly remuneration for maximum temperature divergence of 1:", min_value=0, max_value=300, key="a")
#[[]]    v2g_mon15 = st.slider("Monthly remuneration for required average plug-in of 15h/day :", min_value=0, max_value=300, key="c")

st.subheader("Heat Pump with Thermal Storage")
st.write("*In this scheme, you will have a thermal storage tank installed in your house. This will allow you to keep heating entirely according to your preferences (from the tank), while a third party can flexibly heat up the tank.*")
hpts1m2 = st.slider("How much (in US$) would you expect to be paid monthly to participate in a thermal storage scheme where a storage tank that occupies **1 square meter** (10.8 square feet) would be installed in your home?", min_value=0, max_value=300, key="hpts1m2")
hpts2m2 = st.slider("How much (in US$) would you expect to be paid monthly to participate in a thermal storage scheme where a storage tank that occupies **2 square meter** (21.6 square feet) would be installed in your home?", min_value=0, max_value=300, key="hpts2m2")

if st.checkbox("Include minimum participation terms for V2G (\$12/month) and Smart charging (\$5/month)", key="paper"):
     x = True
else:
     x = False
     
#ss

def change():
    ss.resultsdisplaystate = False
    resetfunc()

#def save_everything():
     #newdf = pd.read_csv("C:/Users/simon/local python/data_collection.csv")
     #dfnew = pd.DataFrame({"V2G10h": [ss.v2g_mon5], "V2G15h": [ss.v2g_mon15], "SC10h": [ss.sc_mon5], "SC15h": [ss.sc_mon15], "HPTS1m2": [ss.hpts1m2], "HPTS2m2": [ss.hpts2m2], "TimestampX": [time.time()]})
     #newnewdf =pd.concat([newdf, dfnew], axis=0)
     #newnewdf.to_csv("C:/Users/simon/local python/data_collection.csv",index=False)

#def update_fig():
#    global fig
#    global ax
#    fig, ax = compute_figure(v2g_mon5,v2g_mon15,
#                   #v2g_freq_5,v2g_freq_15,
#                   sc_mon5,sc_mon15,
#                   #sc_freq_5,sc_freq_15,
#                   1000,hpts1m2,hpts2m2,"Your LCODR Results",x)

# Compute results
if st.button("Compute"):
    #save_everything()
    ss.resultsdisplaystate = True

    ss.fig, ss.ax = compute_figure(v2g_mon5,v2g_mon15,
                   #v2g_freq_5,v2g_freq_15,
                   sc_mon5,sc_mon15,
                   #sc_freq_5,sc_freq_15,
                   1000,hpts1m2,hpts2m2,"Your LCODR Results",x)

if ss.resultsdisplaystate:
    #x, y, z = compute_results(a, a, a)
    #st.write(f"Results: X = {x}, Y = {y}, Z = {z}")

    # Plot the results
    #fig, ax = plt.subplots()
    #ax.bar(["X", "Y", "Z"], [x, y, z])
    #ax.set_ylabel("Values")
    #ax.set_title("Results Bar Graph")
    

    st.pyplot(ss.fig)

    #st.image("Your LCODR results.png", caption="Your LCODR Results")

    email = st.text_input("Enter your email to receive the results:")
    if st.button("Send Email"): 
        #st.write(email)    
                    send_email(email, ss.fig)





    if st.button("Restart",on_click=change):
        #ss.resultsdisplaystate = False
        st.write("Thank you for taking part")
        #ss.resultsdisplaystate = False
    # Email input
#    if st.button("Computer"):
    #x, y, z = compute_results(a, a, a)
    #st.write(f"Results: X = {x}, Y = {y}, Z = {z}")

    # Plot the results
    #fig, ax = plt.subplots()
    #ax.bar(["X", "Y", "Z"], [x, y, z])
    #ax.set_ylabel("Values")
    #ax.set_title("Results Bar Graph")
    #    fig, ax = compute_figure(v2g_mon5,v2g_mon15,
                   #v2g_freq_5,v2g_freq_15,
    #               sc_mon5,sc_mon15,
                   #sc_freq_5,sc_freq_15,
    #               1000,hpts1m2,hpts2m2)

    #    st.pyplot(fig)
    #    if email:
    #        try:
               # send_email(email, (10,11,12))
    #        except Exception as e:
    #            st.error(f"An error occurred while sending the email: {e}")
    #    else:
    #        st.error("Please enter your email address.")

    #st.write(email)
#st.subheader("Heat Pump with Thermal Storage")


