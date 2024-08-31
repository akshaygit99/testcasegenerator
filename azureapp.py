import streamlit as st
import openai
import os
from PIL import Image

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
openai.api_key = OPENAI_API_KEY

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by ChatGPT </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Define the function to generate test cases
def generate_test_cases(requirement, uploaded_image=None):
    # Modify the requirement to include a note about the uploaded image
    if uploaded_image is not None:
        combined_requirement = f"{requirement}\n[Note: Please generate test cases based on the provided requirement and the uploaded image.]"
    else:
        combined_requirement = requirement

    # Call the OpenAI service to generate test cases
    response = openai.ChatCompletion.create(
        model="GPT-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases from uploaded Image"},
            {"role": "user", "content": combined_requirement}
        ]
    )

    return response.choices[0].message.content

# Streamlit app layout
st.title('Test Case Generator :  COE-AI Test')

st.write('Enter your software requirement(s) to generate test cases:')

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150)

# Image upload
st.write('Upload an image:')
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Button to generate test cases
if st.button('Generate Test Cases'):

    if requirement or uploaded_file:

        with st.spinner('Generating...'):

            try:
                # Generate test cases based on the requirement and uploaded image
                test_cases = generate_test_cases(requirement, uploaded_image=uploaded_file)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)

            st.session_state.search_history.append(requirement)

    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')

st.write('Search History:')
st.write(st.session_state.search_history)
