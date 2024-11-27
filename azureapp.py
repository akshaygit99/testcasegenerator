import streamlit as st
import openai
import os
import base64
import pandas as pd
from io import BytesIO

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b>powered by a fine-tuned Open AI model</b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Radio button to choose between Text Input or Uploaded Image
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Function to generate test cases from text
def generate_test_cases(requirement, format_option, template_type=None):
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Test Case Template' and template_type:
        if template_type == 'Jira Template':
            requirement += "\n\n Create test cases with column name as test case id , test case  description , expected result , actual result, execution status, bug severity"
        elif template_type == 'Azure Template':
            requirement += "\n\nGenerate test cases in tabular format with columns: Title, Order, Test Case ID, Assigned To, State."

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases based on fine-tuned inputs."},
            {"role": "user", "content": requirement}
        ]
    )
    return response.choices[0].message['content']

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to create a downloadable Excel file
def create_download_link(dataframe, filename):
    towrite = BytesIO()
    dataframe.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    link = f'<a href="data:file/xlsx;base64,{b64}" download="{filename}.xlsx">Download {filename}</a>'
    return link

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None

# Image upload for generating test cases from an image
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Query for image-based test cases
query = """
You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. 
Analyse this flow diagram and generate software test cases based on this image.
"""

# Dropdown to choose the format, now with "Test Case Template"
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Test Case Template'])

# If the user selects "Test Case Template", allow them to choose between Jira and Azure templates
template_type = None
if format_option == 'Test Case Template':
    template_type = st.radio("Choose a Template:", ['Jira Template', 'Azure Template'])

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Test Case Template' and template_type == 'Jira Template':
                        query += "\n\nCreate test cases with column name as test case id , test case  description , expected result , actual result, execution status, bug severity"
                    elif format_option == 'Test Case Template' and template_type == 'Azure Template':
                        query += "\n\nGenerate test cases in tabular format with columns: Title, Order, Test Case ID, Assigned To, State."

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
                        ]
                    )
                    test_cases = response.choices[0].message['content']
                else:
                    test_cases = generate_test_cases(requirement, format_option, template_type)

                st.success('Generated Test Cases')
                st.write(test_cases)

                # Split the generated test cases into rows for the DataFrame
                rows = [line.strip() for line in test_cases.split('\n') if line.strip()]

                # Handle different formats
                if format_option == 'Test Case Template':
                    if template_type == 'Jira Template':
                        columns = ['Test Case ID', 'Test Case Description', 'Expected Result', 'Actual Result', 'Execution Status', 'Bug Severity']
                    elif template_type == 'Azure Template':
                        columns = ['Title', 'Order', 'Test Case ID', 'Assigned To', 'State']

                    # Create DataFrame
                    try:
                        df = pd.DataFrame([row.split(',') for row in rows], columns=columns)

                        # Provide a download link for the DataFrame as an Excel file
                        download_link = create_download_link(df, f"{template_type.replace(' ', '_')}_Test_Cases")
                        st.markdown(download_link, unsafe_allow_html=True)
                    except Exception as e:
                        st.error("Unable to create the DataFrame. Please check the test case output format.")
                        st.error(e)
                else:
                    st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
