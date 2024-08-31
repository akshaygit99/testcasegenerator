import streamlit as st
import openai
import os
import base64

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
openai.api_key = OPENAI_API_KEY

# Streamlit App UI
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by ChatGPT </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

st.title('Test Case Generator :  COE-AI Test')
st.write('Enter your software requirement(s) to generate test cases or upload an image:')

# Option to choose between Text Input and Image Upload
option = st.radio("Choose input type:", ("Text Requirement", "Upload Image"))

# Function to generate test cases from text
def generate_test_cases(requirement):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
            {"role": "user", "content": requirement}
        ]
    )
    return response.choices[0].message.content

# Function to encode the image as Base64
def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# Input and Button Logic
if option == "Text Requirement":
    requirement = st.text_area("Requirement", height=150)
    
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
        else:
            st.error('Please enter a requirement to generate test cases.')

elif option == "Upload Image":
    uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
    
    if st.button('Generate Test Cases from Image'):
        if uploaded_image:
            with st.spinner('Generating...'):
                try:
                    # Convert image to base64
                    image_data = uploaded_image.read()
                    image_base64 = encode_image(image_data)

                    # OpenAI API call with image data
                    query = """
                    You are an intelligent assistant capable of generating software test cases with the supplied flow diagram.
                    Analyse this flow diagram and generate software test case based on this image.
                    ensure the table is properly formatted and displayed. But dont displays tags in generated test cases
                    Test Case Type should be like Functional, Usability, Compatibility, Performance, etc.
                    Format the response as an HTML table with fixed columns:
                    <table>
                    <tr>
                        <th>Test Case ID</th>
                        <th>Test Case Type</th>
                        <th>Prerequisite</th>
                        <th>Test Scenario</th>
                    </tr>
                    """

                    # OpenAI API payload
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
                        ],
                        max_tokens=1300
                    )

                    test_cases = response.choices[0].message.content
                    st.success('Generated Test Cases')
                    st.write(test_cases)

                except Exception as e:
                    st.error('An error occurred while generating test cases.')
                    st.error(e)
        else:
            st.error('Please upload an image to generate test cases.')

# Show Search History
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

st.write('Search History:')
st.write(st.session_state.search_history)
