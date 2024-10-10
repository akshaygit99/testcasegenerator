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
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b>powered by a fine-tuned Open AI model</b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Radio button to choose between Text Input or Uploaded Image
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Function to generate test cases from text
def generate_test_cases(requirement, format_option):
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    else:
        requirement += "\n\nGenerate the test cases in plain text format."

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases based on fine-tuned inputs."},
            {"role": "user", "content": requirement}
        ],
        temperature=0.7,
        presence_penalty=0.6,
        frequency_penalty=0.3
    )
    return response.choices[0].message['content']

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150) if test_case_source == 'Text Input' else None

# Image upload for generating test cases from an image
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"]) if test_case_source == 'Uploaded Image' else None

# Query for image-based test cases
query = """
You are an intelligent assistant capable of generating software test cases with the supplied flow diagram. 
Analyse this flow diagram and generate software test cases based on this image.
"""

# Dropdown to choose the format
format_option = st.selectbox('Choose Test Case Format', ['BDD', 'NON-BDD'])

# New Section for Test Case Templates
template_type = st.radio("Choose Test Case Template:", ['None', 'Jira Template', 'Azure Template'])

# Function to generate test cases in a tabular format
def generate_test_cases_in_tabular_format(template_type):
    if template_type == 'Jira Template':
        header = ["Test Case ID", "Test Case Summary", "Test Steps", "Expected Result", "Priority"]
    elif template_type == 'Azure Template':
        header = ["Test Case ID", "Test Case Title", "Action Steps", "Expected Result", "Severity"]

    # Generate dummy data for the table (You can replace this with your AI-generated test cases)
    data = [
        ["TC-001", "Login functionality", "Enter username and password", "User is logged in", "High"],
        ["TC-002", "Logout functionality", "Click on logout button", "User is logged out", "Medium"]
    ]

    # Create table in Streamlit
    st.table([header] + data)

# Button to generate test cases
if st.button('Generate Test Cases'):
    if template_type != 'None':
        st.success(f"Generating Test Cases in {template_type} format...")
        generate_test_cases_in_tabular_format(template_type)
    elif (requirement and test_case_source == 'Text Input') or (uploaded_image and test_case_source == 'Uploaded Image'):
        with st.spinner('Generating...'):
            try:
                if test_case_source == 'Uploaded Image' and uploaded_image:
                    image_base64 = encode_image(uploaded_image)
                    if format_option == 'BDD':
                        query += "\n\nGenerate the test cases in Gherkin syntax."
                    else:
                        query += "\n\nGenerate the test cases in plain text format."

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
                        temperature=0.7,
                        presence_penalty=0.6,
                        frequency_penalty=0.3,
                        max_tokens=1300
                    )
                    test_cases = response.choices[0].message['content']
                else:
                    test_cases = generate_test_cases(requirement, format_option)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)
    else:
        st.error('Please enter a requirement or upload an image to generate test cases.')

# Display search history
st.write('Search History:')
st.write(st.session_state.get('search_history', []))
