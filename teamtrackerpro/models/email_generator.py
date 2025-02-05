from bs4 import BeautifulSoup

class EmailGenerator:
    @staticmethod
    def generate_followup(employee: dict, summary_text: str, calls: int, tickets: int, call_goal: str, ticket_goal: str) -> str:
        call_result = f"{calls} / {call_goal}"
        ticket_result = f"{tickets} / {ticket_goal}"

        email_template = f"""
        <html>
        <head>
        <style>
        body {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        color: #333;
        }}
        </style>
        </head>
        <body>
        <p>Dear {employee.get('name', 'Employee')},</p>
        <p>I wanted to follow up on our recent one-on-one meeting. Here is a summary of the review:</p>
        <p>{summary_text}</p>
        <p><b>Goal Achievement:</b><br>
        Calls: {call_result}<br>
        Tickets: {ticket_result}</p>
        <p>If you have any questions or would like to discuss this further, please feel free to reach out.</p>
        <p>Best regards,<br>[Your Name]</p>
        </body>
        </html>
        """
        return email_template

    @staticmethod
    def extract_text_from_html(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()