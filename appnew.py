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


client = ImageAnalysisClient(
  endpoint = AZURE_CV_ENDPOINT,
  credential = AzureKeyCredential(AZURE_CV_KEY)
)

uploaded_image = st.file_uploader("Upload an image to analyze (optional)", type=["jpg", "jpeg", "png"])

if uploaded_image:
  image = Image.open(uploaded_image)
  st.image(image, caption='Uploaded Image')

  imageBytes = io.BytesIO()
  image.save(imageBytes, format=image.format)
  imageBytes = imageBytes.getvalue()


if st.button('Analyse Image'):
  try:
      visual_features = [
        VisualFeatures.TAGS,
        VisualFeatures.CAPTION,
        VisualFeatures.DENSECAPTIONS
      ]
      result = client.analyze_from_url(
      image_url="https://learn.microsoft.com/azure/ai-services/computer-vision/media/quickstarts/presentation.png",
      visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
      gender_neutral_caption=True,  # Optional (default is False)
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
