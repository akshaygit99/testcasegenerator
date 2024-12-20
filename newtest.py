import streamlit as st
import openai
import os
import base64
import pandas as pd
from io import BytesIO

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
def generate_test_cases(requirement, format_option):
    # Append additional instructions based on format
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "ID (leave this column empty), Work Item Type (set to 'Test Case'), Title, Test Step, Step Action, and Step Expected. "
            "Ensure each test case contains more than one test step."
        )
    elif format_option == 'Jira Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Description, Test Name, Test Step, Test Data, and Expected Result. "
            "Ensure each test case contains more than one test step."
            "For the steps, ensure they dont have <br> tags"
        )
    elif format_option == 'Test Rail Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Title, Automated?, Automation Type, Expected Result, Preconditions, Priority, References, Section, Steps, Steps (Additional Info)"
            "For the steps, ensure they dont have <br> tags"
        )

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
                  {"role": "user", "content": requirement}]
    )
    return response.choices[0].message['content']

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to create a downloadable link for Excel files
def create_download_link(dataframe, filename):
    towrite = BytesIO()
    dataframe.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    link = f'<a href="data:file/xlsx;base64,{b64}" download="{filename}.xlsx">Download {filename}</a>'
    return link

# Input for text-based or image-based test case generation
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Dropdown for format selection
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template', 'Test Rail Template'])

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)

                    # Add format instructions to the query
                    query = (
                        "You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. "
                        "Analyse this flow diagram and generate software test cases based on this image."
                    )
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Azure Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "ID (leave this column empty), Work Item Type (set to 'Test Case'), Title, Test Step, Step Action, and Step Expected. "
                            "Ensure each test case contains more than one test step."
                        )
                    elif format_option == 'Jira Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "Description, Test Name, Test Step, Test Data, and Expected Result. "
                            "Ensure each test case contains more than one test step."
                            "For the steps, ensure they dont have <br> tags"
                        )
                    elif format_option == 'Test Rail Template':
                        query += (
                            "\n\nGenerate the test cases in a tabular format with the following columns: "
                            "Title, Automated?, Automation Type, Expected Result, Preconditions, Priority, References, Section, Steps, Steps (Additional Info)"
                            "For the steps, ensure they dont have <br> tags"
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
                        ]
                    )
                    test_cases = response.choices[0].message['content']
                else:
                    # Generate from text input
                    test_cases = generate_test_cases(requirement, format_option)

                st.success('Generated Test Cases')
                st.write(test_cases)

                # Split lines and parse dynamically into a DataFrame
                rows = [line.strip().split(',') for line in test_cases.split('\n') if line.strip()]
                df = pd.DataFrame(rows)

                # Generate the downloadable file based on the format option
                if format_option in ['Azure Template', 'Jira Template']:
                    download_link = create_download_link(df, "test_cases")
                else:
                    # For Test Rail Template (CSV)
                    csv_data = df.to_csv(index=False, header=False)  # Save to CSV without header
                    b64 = base64.b64encode(csv_data.encode()).decode()
                    download_link = f'<a href="data:file/csv;base64,{b64}" download="test_cases.csv">Download test_cases.csv</a>'

                st.markdown(download_link, unsafe_allow_html=True)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
