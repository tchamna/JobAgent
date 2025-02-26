import os
import smtplib
import schedule
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
import openai  # OpenAI for AI-powered job search
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Load environment variables
load_dotenv(override=True)

# OpenAI Configuration (Use GPT-3.5-Turbo for lower cost)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.Client(api_key=OPENAI_API_KEY)  # ✅ Correct OpenAI API usage
OPENAI_MODEL = "gpt-3.5-turbo"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TCHAMNA = os.getenv("EMAIL_TCHAMNA")
EMAIL_DEUKAM = os.getenv("EMAIL_DEUKAM")

prompt_data_science_energy = """
    Generate exactly 5 realistic and current job listings for Data Science and Data Analyst roles in the Energy sector in New Jersey. Format each job listing precisely as shown in HTML below:

    <div style="margin-bottom: 20px;">
        <h3 style="color: #1a73e8;">Job Title: [Insert Job Title]</h3>
        <p><strong>Company:</strong> [Insert Company Name]</p>
        <p><strong>Location:</strong> [Insert City, State]</p>
        <p><strong>Description:</strong> [Insert Short Job Description]</p>
        <p><a href="[Insert Job Link]" style="color: #1a73e8;">Apply Here</a></p>
    </div>

    Ensure that the job titles, companies, and job descriptions are **realistic** and follow industry standards. The links should be plausible job application links or **Google search queries** for similar roles if a direct link is not available.
    """  
    

prompt_chemistry_job = """
    Generate exactly 5 realistic and current job listings for Chemistry roles suitable for someone with a Master's degree in Chemistry in New Jersey. Format each job listing precisely as shown in HTML below:
    <div style="margin-bottom: 20px;">
        <h3 style="color: #1a73e8;">Job Title: [Insert Job Title]</h3>
        <p><strong>Company:</strong> [Insert Company Name]</p>
        <p><strong>Location:</strong> [Insert City, State]</p>
        <p><strong>Description:</strong> [Insert Short Job Description]</p>
        <p><a href="[Insert Job Link]" style="color: #1a73e8;">Apply Here</a></p>
    </div>

    Ensure that the job titles, companies, and job descriptions are **realistic** and follow industry standards. The links should be plausible job application links or **Google search queries** for similar roles if a direct link is not available.
    """  

def format_job_listings(job_listings_text):
    """Formats job listings into structured HTML for email."""
    
    jobs = job_listings_text.split("\n\n")  # Split each job listing
    formatted_jobs = ""

    for job in jobs:
        lines = job.split("\n")
        job_data = {}

        for line in lines:
            if "**Job Title**:" in line:
                job_data["title"] = line.replace("**Job Title**: ", "").strip()
            elif "**Company**:" in line:
                job_data["company"] = line.replace("**Company**: ", "").strip()
            elif "**Location**:" in line:
                job_data["location"] = line.replace("**Location**: ", "").strip()
            elif "**Job Description**:" in line:
                job_data["description"] = line.replace("**Job Description**: ", "").strip()
            elif "**Apply Link**:" in line:
                job_data["link"] = line.replace("**Apply Link**: ", "").strip()

        # Ensure apply link is valid, otherwise, default to Google search query
        apply_link = job_data.get("link", "#")
        if apply_link.lower() == "n/a":
            apply_link = f"https://www.google.com/search?q={job_data['title'].replace(' ', '+')}+job"

        formatted_jobs += f"""
        <div style="font-family: Arial, sans-serif; border-bottom: 1px solid #ddd; padding: 10px;">
            <h3 style="color: #0056b3;">{job_data.get('title', 'N/A')}</h3>
            <p><strong>Company:</strong> {job_data.get('company', 'N/A')}</p>
            <p><strong>Location:</strong> {job_data.get('location', 'N/A')}</p>
            <p><strong>Job Description:</strong> {job_data.get('description', 'N/A')}</p>
            <p><a href="{apply_link}" style="color: #007bff; text-decoration: none;">🔗 Apply Here</a></p>
        </div>
        """

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #333;">🔥 AI-Powered Job Listings: Data Science & Energy</h2>
        {formatted_jobs}
    </body>
    </html>
    """

def fetch_job_listings(prompt):
    """Fetches job listings with clickable links using OpenAI."""
    
   

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000  # Ensure the response is large enough to include all jobs
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "<p>No job listings found due to an API error.</p>"


def send_email(job_listings, email_receiver):
    """Sends an HTML-formatted email with clickable links."""
    if "No job listings" in job_listings:
        print("No new job listings found.")
        return

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #333;">AI-Powered Job Listings: Data Science & Energy</h2>
        {job_listings}
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg["From"] = EMAIL_SENDER
    msg["To"] = email_receiver
    msg["Subject"] = "AI-Powered Job Listings: Data Science & Energy"

    # Ensure job_listings are wrapped properly in HTML
    html_part = MIMEText(job_listings, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email_receiver, msg.as_string())
        server.quit()
        print("✅ Job email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def job_agent_data_science_job():
    """Main job agent function using AI to fetch and send job listings."""
    job_listings = fetch_job_listings(prompt_data_science_energy)
    send_email(job_listings, EMAIL_TCHAMNA)

def job_agent_chemistry_job():
    """Main job agent function using AI to fetch and send job listings."""
    job_listings = fetch_job_listings(prompt_chemistry_job)
    send_email(job_listings, EMAIL_DEUKAM)

# Scheduling the script to run at 6 AM New Jersey time
def schedule_job(time_to_start="06:00"):
    nj_time = pytz.timezone("America/New_York")  # ✅ New Jersey time zone

    def run_job():
        now = datetime.now(nj_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Running job at {now} (New Jersey time)")
        job_agent_data_science_job()
        job_agent_chemistry_job()

    schedule.every().day.at(time_to_start).do(run_job)  # ✅ Schedule for 6 AM NJ time

    while True:
        schedule.run_pending()
        time.sleep(60)  # ✅ Check every minute if it's time to run the job

if __name__ == "__main__":
    print("🚀 Job Scheduler Started! Running every day at 6 AM New Jersey time.")
    schedule_job()
    
    # job_agent_data_science_job()  # Run immediately on script start
    # job_agent_chemistry_job()  # Run immediately on script start
