import streamlit as st
import openai
import io
import os
from PIL import Image
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential


# Set your Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_base = "https://centriinternalgpt.openai.azure.com/"
openai.api_version = "2024-03-01-preview"
openai.api_key = "ed16d540ad3f44bba0656e606a943437"


# Set your Azure Computer Vision API credentials
AZURE_CV_KEY = "7f40f7e9afe94109ab10a49cd83e31b5" 
AZURE_CV_ENDPOINT = "https://tcg-cv.cognitiveservices.azure.com/" 

deployment_name = "centricinteralgpt4"

client = ImageAnalysisClient(
  endpoint = AZURE_CV_ENDPOINT,
  credential = AzureKeyCredential(AZURE_CV_KEY)
)

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by Azure OpenAI </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Create and configure a chat display area
st.title('Test Case Generator :  COE-AI Test')

st.write('Enter your software requirement(s) to generate test cases :')

st.link_button("Centric India - AI Tool Usage Policy ", "https://centricconsultingllc.sharepoint.com/sites/CentricIndia/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR%2FCentric%20India%20AI%20Tool%20Usage%20Policy%5F2023%2Epdf&parent=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR")

requirement = st.text_area("Requirement", height=150)
uploaded_image = st.file_uploader("Upload an image to analyze (optional)", type=["jpg", "jpeg", "png"])

if uploaded_image:
  image = Image.open(uploaded_image)
  st.image(image, caption='Uploaded Image')

imageBytes = io.ByteIO()
image.save(imageBytes, format=image.format)
imageBytes = imageBytes.getvalue()


if st.button('Analyse Image'):
  try:
      visual_features = [
        VisualFeatures.TAGS,
        VisualFeatures.CAPTION,
        VisualFeatures.DENSECAPTIONS
      ]
    result = client.analyze(
      image_data = imageBytes,
      visual_features = visual_features
    )
    if result.caption:
      st.write("Caption:")
      st.write(f'{result.caption.text}')
      st.write(f'{result.caption.confidence:.4f}')
    if len(result.dense_captions.list) >0:
      st.write('Dense Captions ')
      st.dataframe(result.dense_captions.list)
  except:
    pass



def generate_test_cases(requirement):
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": requirement}

        ],
        max_tokens=500
    )
    return response.choices[0]['message']['content'].strip()

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if st.button('Generate Test Cases'):

    if requirement:

        with st.spinner('Generating...'):

            try:
                
                test_cases = generate_test_cases(requirement)

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
