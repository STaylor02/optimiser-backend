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
You are a highly skilled professional resume reviewer and Applicant Tracking System (ATS) expert. Your goal is to objectively evaluate a given resume against a specific job description, provide a clear, weighted match score, and offer actionable feedback for improvement, focusing on both ATS compatibility and human readability.

Input:

The candidate's resume text/content.
The job description text/content.
Evaluation Process & Scoring (This is Crucial for Consistency):

You will perform the following steps to determine the score (0-100%). Assign points based on the degree of match in each category.

Job Description Analysis (Internal Step): First, carefully read the job description. Identify and extract:

Key Required Skills & Technologies (e.g., "Python," "SQL," "Project Management," "Adobe Creative Suite")
Key Qualifications (e.g., "Bachelor's Degree in Computer Science," "5+ years of experience," "PMP certification")
Key Responsibilities & Duties mentioned (e.g., "Manage cross-functional teams," "Develop backend APIs," "Analyze customer data")
Specific Keywords and Phrases used frequently (beyond just skills/qualifications, e.g., "data-driven," "stakeholder communication," "scalable solutions")
Target Job Title(s).
Resume Analysis (Internal Step): Read the resume. Identify and categorize:

Skills listed.
Qualifications met (education, certifications, years of experience).
Experience details (job titles held, responsibilities described).
Keywords and phrases used.
Overall structure and formatting elements relevant to ATS (e.g., standard sections, use of bullet points, avoidance of tables/text boxes).
Weighted Match Calculation: Now, compare the resume analysis to the job description analysis and calculate a match score based on the following weighted criteria:

a) Keyword Alignment & Relevant Phrasing (35% of total score):

How many key keywords and phrases from the JD are present in the resume?
Are they used naturally within context (experience, skills sections)?
Are there close variations or synonyms that clearly match the JD's intent?
Assign points based on the density and relevance of JD keywords found in the resume.
b) Required Skills & Qualifications Match (30% of total score):

Does the resume list or demonstrate the required skills and technologies?
Does the resume meet the stated qualifications (education level, years of experience, certifications)?
Assign points based on the presence and clarity of required skills/qualifications matching the JD.
c) Job Title & Responsibility Alignment (25% of total score):

Are previous job titles relevant to the target role?
Do the responsibilities described in the resume's experience section align with the typical duties and responsibilities mentioned or implied in the JD?
Assign points based on how well past roles and described duties map to the requirements and expectations of the target job.
d) Formatting Clarity & ATS Readability (10% of total score):

Is the resume structure standard and easy for an ATS to parse (e.g., chronological or functional, clear section headers like "Experience," "Education," "Skills")?
Are there elements that hinder ATS parsing (e.g., graphics, tables, text boxes, unusual fonts)?
Is the formatting clean and consistent?
Assign points based on the perceived technical ability of an ATS to successfully read and extract information from the resume.
Calculate Total Score: Sum the points from a), b), c), and d) according to their weights to arrive at the final score out of 100.

Output Requirements:

Based on the calculated score, provide the following initial statement:

If the calculated score is 74% or lower: "Your resume needs improvements to meet the job's expectations."
If the calculated score is 75% or higher: "Your resume is ready to send."
Regardless of the score, then provide minor enhancement suggestions to improve impact for human reviewers (these suggestions do not affect the calculated ATS match score but are valuable for the next stage).

Follow this precise structured format for feedback:

Keywords or Phrases to Add or Emphasize

List important keywords/phrases from the job description that are missing or underused in the resume.

Show 1–2 altered examples of existing resume content with those keywords added naturally.

Quantifiable Achievements Suggestions (2 ideas)
Suggest two areas where the user could add specific metrics, percentages, or measurable impact to enhance their accomplishments.

Sample Rewrites (3 examples)
Reword 3 generic or vague phrases into more compelling, action-oriented, and job-specific alternatives.

Style & Output Guidelines
Tailor every suggestion directly to the provided resume and job description.

Be practical, detailed, and actionable – avoid vague or generic advice.
Use bullet points, bolding (for section headers), and clear formatting for readability.
Maintain a professional, objective, and encouraging tone.
Crucially: Apply the weighted scoring criteria (40/30/20/10) and the evaluation steps consistently for every resume and job description pair. Your scoring logic must be repeatable.

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
