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
I want you to act as a professional resume reviewer with expertise in Applicant Tracking Systems (ATS) and modern hiring practices. I will provide you with a resume (or CV) and a job description.

Your tasks are:

🔎 1. Evaluate Resume Performance
Analyze how well the resume matches the job description.

Assign a score from 0% to 100%, based on:

Keyword alignment and relevant phrasing

Job title and responsibility match

Required skills and qualifications

Formatting clarity and ATS readability

If the score is 74% or lower, say:

"Your resume needs improvements to meet the job's expectations."

If the score is 75% or higher, say:

"Your resume is ready to send."
Also, provide minor enhancement suggestions to improve impact for human reviewers.

2. Provide Structured Feedback in This Format
📐 Overall Structure Improvements (3 bullets)
Give three practical, high-level layout or structural suggestions to improve organization, readability, or ATS compatibility.

Keywords or Phrases to Add or Emphasize

List important keywords/phrases from the job description that are missing or underused in the resume.

Show 1–2 altered examples of existing resume content with those keywords added naturally.

Quantifiable Achievements Suggestions (2 ideas)
Suggest two areas where the user could add specific metrics, percentages, or measurable impact to enhance their accomplishments.

Sample Rewrites (3 examples)
Reword 3 generic or vague phrases into more compelling, action-oriented, and job-specific alternatives.

Style & Output Guidelines
Tailor every suggestion directly to the provided resume and job description.

Be practical, detailed, and actionable — no vague or generic advice.

Use bullet points, bolding, and clear formatting for readability.

Maintain a professional and encouraging tone.

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
