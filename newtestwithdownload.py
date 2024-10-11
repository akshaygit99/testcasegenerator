import streamlit as st
import openai
import os
import base64
import pandas as pd
import io

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
        requirement += "\n\nGenerate the test cases in a tabular format with the following columns: Title, Work Item Type, Test Step, Step Action, and Step Executed."
    elif format_option == 'Jira Template':
        requirement += "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data, and Expected Result."

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
Analyze this flow diagram and generate software test cases based on this image.
"""

# Dropdown to choose the format
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template'])

# Function to convert test cases to DataFrame for Azure/Jira templates
def test_cases_to_dataframe(test_cases, format_option):
    if format_option == 'Azure Template':
        columns = ['Title', 'Work Item Type', 'Test Step', 'Step Action', 'Step Executed']
    elif format_option == 'Jira Template':
        columns = ['Description', 'Test Name', 'Test Step', 'Test Data', 'Expected Result']
    
    data = [row.split(",") for row in test_cases.split("\n") if row]  # Example logic, adjust based on actual response format
    df = pd.DataFrame(data, columns=columns)
    return df

# Function to download the DataFrame as an Excel file
def download_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Button to generate test cases
if st.button('Generate Test Cases'):
    if (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)

                    # Add the format instructions to the query when generating test cases from the image
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    elif format_option == 'NON-BDD':
                        query += "\n\nGenerate the test cases in plain text format."
                    elif format_option == 'Azure Template':
                        query += "\n\nGenerate the test cases in a tabular format with the following columns: Title, Work Item Type, Test Step, Step Action and Step Executed."
                    elif format_option == 'Jira Template':
                        query += "\n\nGenerate the test cases in a tabular format with the following columns: Description, Test Name, Test Step, Test Data and Expected Result."

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
                    # If generating from text input, handle with the generate_test_cases function
                    test_cases = generate_test_cases(requirement, format_option)

                st.success('Generated Test Cases')
                st.write(test_cases)

                # Provide download option if Azure or Jira template is chosen
                if format_option in ['Azure Template', 'Jira Template']:
                    df = test_cases_to_dataframe(test_cases, format_option)
                    excel_data = download_excel(df)

                    st.download_button(
                        label="Download Test Cases as Excel",
                        data=excel_data,
                        file_name=f"{format_option}_Test_Cases.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')
