import streamlit as st
import openai
import os
import base64

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b> powered by Open AI Akshay </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Checkbox to choose between Text or Image-based test cases
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Define the function to generate test cases from text
def generate_test_cases(requirement, format_option):
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
        requirement += "\n\nGenerate the test cases in a tabular format with the following columns: Title, Work Item Type, Test Step, Step Action and Step Executed"
    elif format_option == 'Jira Template':
        requirement += "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data and Expected Result"

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

# Text area for user to enter the software requirement (only for text input case)
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None

# Image upload for generating test cases from an image
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Query for image-based test cases
query = """
You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. 
Analyse this flow diagram and generate software test cases based on this image.
"""

# ==================== Updated Section Starts Here ====================

# Primary dropdown to choose the format
main_format_option = st.selectbox(
    'Choose Test Case Format',
    ['BDD', 'NON-BDD', 'Test Case Template']
)

# Initialize format_option based on user selection
format_option = None
if main_format_option == 'Test Case Template':
    st.write("Select one of the following templates:")
    azure_template = st.checkbox('Azure Template')
    jira_template = st.checkbox('Jira Template')

    # Ensure that only one template is selected
    if azure_template and not jira_template:
        format_option = 'Azure Template'
    elif jira_template and not azure_template:
        format_option = 'Jira Template'
    elif azure_template and jira_template:
        st.error("Please select only one template (Azure or Jira).")
else:
    format_option = main_format_option

# ==================== Updated Section Ends Here ====================

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        if format_option:
            with st.spinner('Generating...'):
                try:
                    if test_case_source == 'Uploaded Image' and uploaded_image:
                        image_base64 = encode_image(uploaded_image)

                        # Add the format instructions to the query when generating test cases from the image
                        if format_option == 'BDD':
                            modified_query = query + "\n\nGenerate the test cases in Gherkin syntax."
                        elif format_option == 'NON-BDD':
                            modified_query = query + "\n\nGenerate the test cases in plain text format."
                        elif format_option == 'Azure Template':
                            modified_query = query + "\n\nGenerate the test cases in a tabular format with the following columns: Title, Work Item Type, Test Step, Step Action and Step Executed"
                        elif format_option == 'Jira Template':
                            modified_query = query + "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data and Expected Result"

                        response = openai.ChatCompletion.create(
                            model="gpt-4-turbo",
                            messages=[
                                {
                                    "role": "user",
                                    "content": modified_query
                                },
                                {
                                    "role": "user",
                                    "content": f"![Flow Diagram](data:image/png;base64,{image_base64})"
                                }
                            ],
                            max_tokens=1300
                        )
                        test_cases = response.choices[0].message['content']
                    else:
                        # If generating from text input, handle with the generate_test_cases function
                        test_cases = generate_test_cases(requirement, format_option)

                    st.success('Generated Test Cases')
                    st.write(test_cases)

                except Exception as e:
                    st.error('An error occurred while generating test cases.')
                    st.error(e)
        else:
            st.error('Please select a format or template to generate test cases.')
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
