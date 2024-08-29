import streamlit as st
import openai
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
from io import BytesIO

# Set your Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_base = "https://centriinternalgpt.openai.azure.com/"
openai.api_version = "2024-03-01-preview"
openai.api_key = "ed16d540ad3f44bba0656e606a943437" # Replace with your Azure OpenAI API key

# Set your Azure Computer Vision API credentials
AZURE_CV_KEY = "7f40f7e9afe94109ab10a49cd83e31b5"  # Replace with your Azure Computer Vision key
AZURE_CV_ENDPOINT = "https://tcg-cv.cognitiveservices.azure.com/"  # Replace with your Azure Computer Vision endpoint

# Initialize Azure Computer Vision client
computervision_client = ComputerVisionClient(AZURE_CV_ENDPOINT, CognitiveServicesCredentials(AZURE_CV_KEY))

deployment_name = "centricinteralgpt4"

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by Azure OpenAI </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

st.title('Test Case Generator : COE-AI Test')
st.write('Enter your software requirement(s) to generate test cases :')
st.link_button("Centric India - AI Tool Usage Policy", "https://centricconsultingllc.sharepoint.com/sites/CentricIndia/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR%2FCentric%20India%20AI%20Tool%20Usage%20Policy%5F2023%2Epdf&parent=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR")

requirement = st.text_area("Requirement", height=150)
uploaded_image = st.file_uploader("Upload an image to analyze (optional)", type=["jpg", "jpeg", "png"])

def describe_image(image_data):
    """Describe the uploaded image using Azure Computer Vision API."""
    image = Image.open(BytesIO(image_data))
    description_result = computervision_client.describe_image_in_stream(image)
    
    if description_result.captions:
        return " ".join([caption.text for caption in description_result.captions])
    else:
        return "No description available for the image."





def generate_test_cases(requirement, image_description=None):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": requirement}
    ]
    
    if image_description:
        messages.append({"role": "user", "content": f"Additional context based on the uploaded image: {image_description}"})
    
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if st.button('Generate Test Cases'):
    if requirement:
        with st.spinner('Generating...'):
            try:
                image_description = None
                if uploaded_image is not None:
                    image_data = uploaded_image.read()
                    # image_description = analyze_image(image_data)
                    st.write(f"Image description: {image_description}")
                
                test_cases = generate_test_cases(requirement, image_description)
                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)

            st.session_state.search_history.append(requirement)

    else:
        st.error('Please enter a requirement to generate test cases.')

st.write('Search History:')
st.write(st.session_state.search_history)
