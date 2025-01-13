import streamlit as st
import openai
import os
import base64
import pandas as pd
from io import BytesIO
from flask import Flask, request
import threading
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Flask App for Capturing Client IP
flask_app = Flask(__name__)

@flask_app.route('/')
def log_ip():
    client_ip = request.remote_addr
    with open("client_ips.log", "a") as log_file:
        log_file.write(f"{client_ip}\n")
    return f"Client IP Address: {client_ip}"

# Function to run Flask app
def run_flask():
    flask_dispatch = DispatcherMiddleware(flask_app)
    run_simple('0.0.0.0', 5000, flask_dispatch, use_reloader=False)

# Start Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Retrieve the OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Streamlit UI Design
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b>powered by OpenAI</b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Sidebar Section for Downloading Client Logs
st.sidebar.title("Client Logs")
if os.path.exists("client_ips.log"):
    with open("client_ips.log", "r") as log_file:
        logs = log_file.read()
    
    # Add a download button to the sidebar
    st.sidebar.download_button(
        label="Download Client Logs",
        data=logs,
        file_name="client_ips.log",
        mime="text/plain",
    )
else:
    st.sidebar.write("No client logs available yet.")

# Checkbox to choose between Text or Image-based test cases
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Define the function to generate test cases
def generate_test_cases(requirement, format_option):
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "ID (leave this column empty), Work Item Type (set to 'Test Case'), Title, Test Step, Step Action, and Step Expected. "
            "Ensure each test case contains more than one test step."
        )
    elif format_option == 'Jira Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Description, Test Name, Test Step, Test Data, and Expected Result. "
            "Ensure each test case contains more than one test step."
        )
    elif format_option == 'Test Rail Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Title, Automated?, Automation Type, Expected Result, Preconditions, Priority, References, Section, Steps, Steps (Additional Info)."
        )
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
                  {"role": "user", "content": requirement}]
    )
    return response.choices[0].message['content']

# Input for text-based or image-based test case generation
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Dropdown for format selection
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template', 'Test Rail Template'])

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = base64.b64encode(uploaded_image.read()).decode('utf-8')
                    query = (
                        "You are an intelligent assistant capable of generating software test cases based on the supplied flow diagram. "
                        "Analyze this flow diagram and generate software test cases based on the image provided."
                    )
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Azure Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "ID, Work Item Type, Title, Test Step, Step Action, and Step Expected."
                        )
                    elif format_option == 'Jira Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "Description, Test Name, Test Step, Test Data, Expected Result."
                        )
                    elif format_option == 'Test Rail Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "Title, Automated?, Automation Type, Expected Result, Preconditions, Priority, References, Section, Steps, Steps (Additional Info)."
                        )

                    # OpenAI ChatCompletion API call
                    response = openai.ChatCompletion.create(
                        model="gpt-4-turbo",
                        messages=[
                             {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": query},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                                ]
                            }
                        ]
                    )
                    test_cases = response.choices[0].message['content']
                else:
                    test_cases = generate_test_cases(requirement, format_option)

                st.success('Generated Test Cases')
                st.write(test_cases)

                # Download link for test cases
                rows = [line.split(',') for line in test_cases.split('\n') if line.strip()]
                df = pd.DataFrame(rows)
                towrite = BytesIO()
                df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                b64 = base64.b64encode(towrite.read()).decode()
                link = f'<a href="data:file/xlsx;base64,{b64}" download="test_cases.xlsx">Download Test Cases</a>'
                st.markdown(link, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
