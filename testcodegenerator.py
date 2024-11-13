import streamlit as st

# Function to generate boilerplate test code based on language
def generate_test_code(requirement, language):
    if language == "Java":
        code = f"""
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class RequirementTest {{
    @Test
    public void testRequirement() {{
        // Requirement: {requirement}
        // Add your test code logic here

        // Example assertion (customize as needed)
        assertEquals(true, true);
    }}
}}
"""
    elif language == "Python":
        code = f"""
import unittest

class RequirementTest(unittest.TestCase):
    def test_requirement(self):
        # Requirement: {requirement}
        # Add your test code logic here

        # Example assertion (customize as needed)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
"""
    elif language == "C#":
        code = f"""
using NUnit.Framework;

[TestFixture]
public class RequirementTest
{{
    [Test]
    public void TestRequirement()
    {{
        // Requirement: {requirement}
        // Add your test code logic here

        // Example assertion (customize as needed)
        Assert.IsTrue(true);
    }}
}}
"""
    else:
        code = "Unsupported language selected."

    return code

# Streamlit app setup
st.title("Test Code Generator")

# Input field for the requirement
requirement = st.text_input("Requirement:", placeholder="Enter the requirement here")

# Dropdown menu to select language
language = st.selectbox("Generate Test Code in:", ["Java", "Python", "C#"])

# Button to generate test code
if st.button("Generate Test Code"):
    if requirement:
        # Generate and display the test code
        test_code = generate_test_code(requirement, language)
        st.code(test_code, language=language.lower())
    else:
        st.warning("Please enter a requirement to generate test code.")
