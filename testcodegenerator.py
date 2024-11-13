import streamlit as st
import openai
import os

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates boilerplate test code based on user requirements <b> powered by Open AI </b>. Select a language to streamline your coding process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150, placeholder="Enter the test requirement here")

# Dropdown to choose the language
language_option = st.selectbox('Generate Test Code in:', ['Java', 'Python', 'C#'])

# Function to generate test code based on requirement and selected language
def generate_test_code(requirement, language):
    prompt = f"Generate boilerplate test code in {language} for the following requirement:\n\n{requirement}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating boilerplate test code based on user requirements in Java, Python, or C#."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

# Button to generate test code
if st.button('Generate Test Code'):
    if requirement:
        with st.spinner('Generating...'):
            try:
                test_code = generate_test_code(requirement, language_option)
                st.success('Generated Test Code')
                st.code(test_code, language=language_option.lower())
            except Exception as e:
                st.error('An error occurred while generating test code.')
                st.error(e)
    else:
        st.error('Please enter a requirement to generate test code.')
