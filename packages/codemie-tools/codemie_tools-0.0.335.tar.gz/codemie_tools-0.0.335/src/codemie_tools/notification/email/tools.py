import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type, Optional, Tuple

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.notification.email.models import EmailToolConfig
from codemie_tools.notification.tools_vars import EMAIL_TOOL


class EmailToolInput(BaseModel):
    recipient_emails: list[str] = Field(None, description="A list of recipient email addresses")
    subject: str = Field(None, description="The email subject")
    body: str = Field(None, description="The body of the email")


class EmailTool(CodeMieTool):
    name: str = EMAIL_TOOL.name
    email_creds: Optional[EmailToolConfig] = Field(exclude=True, default=None)
    args_schema: Type[BaseModel] = EmailToolInput
    description: str = EMAIL_TOOL.description

    def execute(self, recipient_emails: str, subject: str, body: str) -> str:
        if not self.email_creds:
            raise ValueError("Email configuration is not provided.")
        try:
            host, port = self.email_creds.url.split(':')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_creds.smtp_username
            msg['To'] = ", ".join(recipient_emails)

            part = MIMEText(body, 'html')
            msg.attach(part)

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(self.email_creds.smtp_username, self.email_creds.smtp_password)
                server.sendmail(self.email_creds.smtp_username, recipient_emails, msg.as_string())
                server.quit()

            return f"Email sent successfully to {recipient_emails}"
        except Exception as e:
            return f"Failed to send email: {e}"

    def integration_healthcheck(self) -> Tuple[bool, str]:
        if not self.email_creds:
            return False, "Email configuration is not provided."
        try:
            host, port = self.email_creds.url.split(':')
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(self.email_creds.smtp_username, self.email_creds.smtp_password)
                server.noop()
                server.quit()
            return True, ""
        except smtplib.SMTPResponseException as e:
            return False, f"SMTP Code: {e.smtp_code}. SMTP error: {e.smtp_error}"
        except smtplib.SMTPException as e:
            return False, str(e)

