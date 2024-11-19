import streamlit as st
import openai
import os
import base64

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# App header and description
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b>powered by Open AI</b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Radio button to select between Text Input and Uploaded Image
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Function to generate test cases from text input
def generate_test_cases(requirement, format_option):
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "ID, Work Item Type, Title, Test Step, Step Action, and Step Expected. "
            "Use nested numbering for steps (e.g., 1, 1.1, 1.2 for substeps). Ensure the hierarchy matches the given context."
        )
    elif format_option == 'Jira Template':
        requirement += "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data and Expected Result."

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
            {"role": "user", "content": requirement}
        ]
    )
    return response.choices[0].message['content']

# Function to encode an uploaded image into Base64
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Text area for user requirements (for Text Input)
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None

# File uploader for image input (for Uploaded Image)
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Query for generating test cases from an image
query = """
You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. 
Analyse this flow diagram and generate software test cases based on this image.
"""

# Dropdown to select the test case format
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template'])

# Generate button logic
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)

                    # Add specific formatting instructions for Azure Template
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Azure Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "ID, Work Item Type, Title, Test Step, Step Action, and Step Expected. "
                            "Use nested numbering for steps (e.g., 1, 1.1, 1.2 for substeps). Ensure the hierarchy matches the given context."
                        )
                    elif format_option == 'Jira Template':
                        query += "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data and Expected Result."

                    # API call for image-based test cases
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
                    test_cases = response.choices[0].message['content']
                else:
                    # Generate test cases from text input
                    test_cases = generate_test_cases(requirement, format_option)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
