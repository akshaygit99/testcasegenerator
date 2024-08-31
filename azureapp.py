import streamlit as st
import openai
import os
import base64
import requests
from PIL import Image
import io

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Streamlit app layout
st.title('Test Case Generator : COE-AI Test')

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by ChatGPT </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

st.write('Select the format for the test cases:')
format_type = st.selectbox('Choose format', ['BDD', 'NON-BDD'])

st.write('Enter your software requirement(s) to generate test cases:')
requirement = st.text_area("Requirement", height=150)

# Image upload
st.write('Upload an image:')
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Function to generate test cases
def generate_test_cases(requirement, format_type, base64_image=None):
    system_message = "Generate test cases in BDD format." if format_type == "BDD" else "Generate test cases in text format."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Construct the message content
    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": requirement
                }
            ]
        }
    ]

    # If there's an image, add it to the message
    if base64_image:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    # Payload for the API request
    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "max_tokens": 300
    }

    # Send the request to the OpenAI API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Return the response content
    return response.json()

# Button to generate test cases
if st.button('Generate Test Cases'):
    if requirement or uploaded_file:
        with st.spinner('Generating...'):
            try:
                base64_image = None
                if uploaded_file:
                    base64_image = encode_image(uploaded_file)

                # Generate test cases based on the requirement and uploaded image
                test_cases = generate_test_cases(requirement, format_type, base64_image)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')

st.write('Search History:')
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
st.write(st.session_state.search_history)
