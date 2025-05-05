import openai
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_resume(resume_text, job_description):
    prompt = f"""
I want you to act as a professional resume reviewer with expertise in Applicant Tracking Systems (ATS) and hiring best practices. I will provide you with a resume and a job description.

Your tasks are:

1. **Evaluate ATS Compatibility**  
Compare the resume to the job description and assign a performance score between **0% and 100%** based on keyword alignment, job title match, required skills, and formatting readability for ATS.

2. **If the score is below 75%**, provide specific, actionable suggestions to improve it. Your suggestions should include:
- **Keywords and phrases to add or emphasize** from the job description.
- **Suggestions for quantifiable achievements** (use metrics or measurable results where possible).
- **Structural or formatting improvements** to help ATS parsing and visual clarity.
- **Content to remove or condense**, if it doesn’t target the role effectively.
- Clear recommendations like: “Replace ‘supported the team’ with ‘collaborated with 4 cross-functional teams to launch X’”.

3. **If the score is 75% or higher**, confirm that the resume is ready to submit and suggest any final polish or enhancements to make it stand out to human recruiters.

Be direct, practical, and detailed with your feedback.

Resume:
\"\"\"{resume_text}\"\"\"

Job Description:
\"\"\"{job_description}\"\"\"
"""

    try:
        # Use the ChatCompletion API with the correct endpoint
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",  # Replace with "gpt-4" or other model as needed
            messages=[
                {"role": "system", "content": "You are an ATS compatibility reviewer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.7
        )

        # Extract the response from the message field
        full_response = response['choices'][0]['message']['content'].strip()

        # Extract rating from the response using regex
        rating_match = re.search(r'(\d{1,3})\s*%', full_response)
        rating = int(rating_match.group(1)) if rating_match else 0

        # Extract suggestions if under 75
        suggestions = []
        if rating < 75:
            suggestions = [line.strip("- ").strip() for line in full_response.split("\n") if line.startswith("-")]

        return rating, suggestions

    except Exception as e:
        print("Error in analyze_resume:\n", e)
        return 0, ["There was an error analyzing the resume."]
