import streamlit as st
import openai
import os
import base64

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Streamlit UI Design
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b> powered by Open AI </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Checkbox to choose between Text or Image-based test cases
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Define the function to generate test cases
def generate_test_cases(requirement, format_option, id_sequence=None):
    # Append additional instructions based on format
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "ID, Work Item Type, Title, Test Step, Step Action, and Step Expected. "
            "Set 'Work Item Type' to 'Test Case' for every row. Use nested numbering for test steps (e.g., 1, 1.1, 1.2) "
            "and ensure each test case contains more than one test step."
        )
        if id_sequence:
            requirement += f"\n\nUse the following sequence of IDs for test cases: {', '.join(id_sequence)}."
    elif format_option == 'Jira Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Description, Test Name, Test Step, Test Data, and Expected Result. "
            "Ensure each test case contains more than one test step."
        )

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
            {"role": "user", "content": requirement}
        ]
    )
    return response.choices[0].message['content']

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Input for text-based or image-based test case generation
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Query for image-based test cases
query = """
You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. 
Analyse this flow diagram and generate software test cases based on this image.
"""

# Dropdown for format selection
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template'])

# Input for Azure ID sequence
id_sequence = None
if format_option == 'Azure Template':
    id_sequence_input = st.text_input("Enter ID sequence (comma-separated)", value="1, 2, 3")
    if id_sequence_input:
        id_sequence = [id.strip() for id in id_sequence_input.split(",")]

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)

                    # Add format instructions to the query
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Azure Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "ID, Work Item Type, Title, Test Step, Step Action, and Step Expected. "
                            "Set 'Work Item Type' to 'Test Case' for every row. Use nested numbering for test steps "
                            "(e.g., 1, 1.1, 1.2) and ensure each test case contains more than one test step."
                        )
                        if id_sequence:
                            query += f"\n\nUse the following sequence of IDs for test cases: {', '.join(id_sequence)}."
                    elif format_option == 'Jira Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "Description, Test Name, Test Step, Test Data, and Expected Result. "
                            "Ensure each test case contains more than one test step."
                        )

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
                    # Generate from text input
                    test_cases = generate_test_cases(requirement, format_option, id_sequence)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
