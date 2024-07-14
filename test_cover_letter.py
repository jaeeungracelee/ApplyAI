import unittest
from unittest.mock import patch
from main import generate_ai_prompt, get_ai_response, fill_template

class TestCoverLetterGenerator(unittest.TestCase):
    def test_generate_ai_prompt(self):
        user_input = {
            "job_title": "Software Engineer",
            "company_name": "Tech Corp",
            "resume_summary": "Experienced developer with Python and JavaScript skills"
        }
        prompt = generate_ai_prompt(user_input)
        self.assertIn("Software Engineer", prompt)
        self.assertIn("Tech Corp", prompt)

    @patch('main.openai.ChatCompletion.create')
    def test_get_ai_response(self, mock_create):
        mock_create.return_value = {"choices": [{"message": {"content": "This is a test response"}}]}
        prompt = "Write a short cover letter for a Software Engineer position."
        response = get_ai_response(prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 10)

    def test_fill_template(self):
        ai_response = "This is a test cover letter content."
        user_input = {
            "full_name": "John Doe",
            "phone": "123-456-7890",
            "email": "john@example.com",
            "website": "johndoe.com",
            "linkedin": "linkedin.com/in/johndoe",
            "linkedin_username": "johndoe",
            "github": "github.com/johndoe",
            "github_username": "johndoe",
            "company_name": "Tech Corp",
            "company_address": "123 Tech St, San Francisco, CA"
        }
        filled_template = fill_template(ai_response, user_input)
        self.assertIn("John Doe", filled_template)
        self.assertIn("123-456-7890", filled_template)
        self.assertIn("This is a test cover letter content.", filled_template)

if __name__ == '__main__':
    unittest.main()
