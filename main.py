import os
from dotenv import load_dotenv
import openai
from datetime import date
import subprocess
import logging
import sys
import argparse
import time

load_dotenv()

logging.basicConfig(filename='cover_letter_generator.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def generate_ai_prompt(user_input):
    prompt = f"""Please write a cover letter for a {user_input['job_title']} position at {user_input['company_name']}. 
    Use the following information from my resume:
    {user_input['resume_summary']}
    
    Please tailor the cover letter to highlight my most relevant skills and experiences for this specific position. 
    The tone should be professional yet enthusiastic, demonstrating my passion for technology and eagerness to contribute to {user_input['company_name']}.
    """
    return prompt

def get_ai_response(prompt, retries=5, delay=1):
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" 
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes cover letters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                n=1,
                temperature=0.7,
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            if isinstance(e, openai.error.RateLimitError) and attempt < retries - 1:
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                raise

def fill_template(ai_response, user_input):
    with open('latex_template.tex', 'r') as file:
        template = file.read()
    
    filled_template = template.replace('{{FULL_NAME}}', user_input['full_name'])
    filled_template = filled_template.replace('{{PHONE}}', user_input['phone'])
    filled_template = filled_template.replace('{{EMAIL}}', user_input['email'])
    filled_template = filled_template.replace('{{WEBSITE}}', user_input['website'])
    filled_template = filled_template.replace('{{LINKEDIN}}', user_input['linkedin'])
    filled_template = filled_template.replace('{{LINKEDIN_USERNAME}}', user_input['linkedin_username'])
    filled_template = filled_template.replace('{{GITHUB}}', user_input['github'])
    filled_template = filled_template.replace('{{GITHUB_USERNAME}}', user_input['github_username'])
    filled_template = filled_template.replace('{{DATE}}', date.today().strftime("%B %d, %Y"))
    filled_template = filled_template.replace('{{COMPANY_NAME}}', user_input['company_name'])
    filled_template = filled_template.replace('{{COMPANY_ADDRESS}}', user_input['company_address'])
    filled_template = filled_template.replace('{{COVER_LETTER_CONTENT}}', ai_response)
    
    return filled_template

def compile_latex(latex_content):
    with open('cover_letter.tex', 'w') as file:
        file.write(latex_content)
    
    subprocess.run(['pdflatex', 'cover_letter.tex'])
    
    if os.path.exists('cover_letter.pdf'):
        return 'cover_letter.pdf'
    else:
        return None

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a cover letter")
    parser.add_argument("--name", required=True, help="Your full name")
    parser.add_argument("--phone", required=True, help="Your phone number")
    parser.add_argument("--email", required=True, help="Your email address")
    parser.add_argument("--website", required=True, help="Your website URL")
    parser.add_argument("--linkedin", required=True, help="Your LinkedIn URL")
    parser.add_argument("--github", required=True, help="Your GitHub URL")
    parser.add_argument("--job-title", required=True, help="Job title you're applying for")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--company-address", required=True, help="Company address")
    parser.add_argument("--resume-summary", required=True, help="Summary of your resume")
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        user_input = {
            "full_name": args.name,
            "phone": args.phone,
            "email": args.email,
            "website": args.website,
            "linkedin": args.linkedin,
            "linkedin_username": args.linkedin.split("/")[-1],
            "github": args.github,
            "github_username": args.github.split("/")[-1],
            "job_title": args.job_title,
            "company_name": args.company,
            "company_address": args.company_address,
            "resume_summary": args.resume_summary
        }
        
        prompt = generate_ai_prompt(user_input)
        ai_response = get_ai_response(prompt)
        latex_content = fill_template(ai_response, user_input)
        pdf_path = compile_latex(latex_content)

        if pdf_path:
            print(f"Cover letter generated: {pdf_path}")
            logging.info(f"Cover letter generated successfully for {user_input['full_name']}")
        else:
            print("Failed to generate PDF. Please check LaTeX installation and try again.")
            logging.error("Failed to generate PDF")
    except Exception as e:
        logging.error(f"Error generating cover letter: {str(e)}")
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
