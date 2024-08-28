import streamlit as st
import openai
import os
from PIL import Image
import base64
from io import BytesIO
import random

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
openai.api_key = OPENAI_API_KEY

# Streamlit header and description
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by ChatGPT </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Function to generate test cases
def generate_test_cases(requirement):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
            {"role": "user", "content": requirement}
        ]
    )
    return response['choices'][0]['message']['content']

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to convert file to base64
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()
    return base64.b64encode(img_byte).decode('utf-8')

# Function to add image to messages
def add_image_to_messages():
    if st.session_state.uploaded_img or ("camera_img" in st.session_state and st.session_state.camera_img):
        img_type = st.session_state.uploaded_img.type if st.session_state.uploaded_img else "image/jpeg"
        if img_type == "video/mp4":
            # Save the video file
            video_id = random.randint(100000, 999999)
            with open(f"video_{video_id}.mp4", "wb") as f:
                f.write(st.session_state.uploaded_img.read())
            st.session_state.messages.append({
                "role": "user",
                "content": [{"type": "video_file", "video_file": f"video_{video_id}.mp4"}]
            })
        else:
            raw_img = Image.open(st.session_state.uploaded_img or st.session_state.camera_img)
            img = get_image_base64(raw_img)
            st.session_state.messages.append({
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": f"data:{img_type};base64,{img}"}}]
            })

# Streamlit app layout
st.title('Test Case Generator :  COE-AI Test')
st.write('Enter your software requirement(s) to generate test cases :')

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Link to Centric India - AI Tool Usage Policy
st.link_button("Centric India - AI Tool Usage Policy", "https://centricconsultingllc.sharepoint.com/sites/CentricIndia/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR%2FCentric%20India%20AI%20Tool%20Usage%20Policy%5F2023%2Epdf&parent=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR")

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150)

# Image and video upload
st.write(f"### **🖼️ Add an image or a video file:**")

cols_img = st.columns(2)
with cols_img[0]:
    with st.popover("📁 Upload"):
        st.file_uploader(
            "Upload an image or a video:", 
            type=["png", "jpg", "jpeg", "mp4"], 
            accept_multiple_files=False,
            key="uploaded_img",
            on_change=add_image_to_messages,
        )

with cols_img[1]:                    
    with st.popover("📸 Camera"):
        activate_camera = st.checkbox("Activate camera")
        if activate_camera:
            st.camera_input(
                "Take a picture", 
                key="camera_img",
                on_change=add_image_to_messages,
            )

# Button to generate test cases
if st.button('Generate Test Cases'):
    if requirement:
        with st.spinner('Generating...'):
            try:
                test_cases = generate_test_cases(requirement)
                st.success('Generated Test Cases')
                st.write(test_cases)
            except Exception as e:
                st.error(f'An error occurred while generating test cases: {str(e)}')
