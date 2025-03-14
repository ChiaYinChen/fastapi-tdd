import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

from jinja2 import Template

from ..core.config import settings
from ..core.security import encode_url_safe_token

TEMPLATE_FOLDER = Path(__file__).parents[1] / "templates"


class EmailGenerator(ABC):
    @abstractmethod
    def email_template(self) -> str:
        """
        Retrieve the email template file content.

        This method should be implemented to return the HTML content of the email template as a string.
        """
        pass

    @abstractmethod
    def email_subject(self) -> str:
        """Abstract method to define email subject."""
        pass

    @abstractmethod
    def email_context(self, *args, **kwargs) -> dict:
        """Abstract method to generate email context data for rendering the email template."""
        pass

    def generate_email(self, recipients: list[str], *args, **kwargs) -> MIMEMultipart:
        """Construct an email message with the specified template and context."""
        message = MIMEMultipart("alternative")
        message["Subject"] = self.email_subject()

        sender_name = kwargs.get("sender_name")
        if not sender_name:
            message["From"] = settings.MAIL_SENDER
        else:
            message["From"] = formataddr((sender_name, settings.MAIL_SENDER))

        message["To"] = ",".join(recipients)
        if cc := kwargs.get("cc"):
            message["Cc"] = ",".join(cc)

        template = Template(self.email_template())
        context = self.email_context(*args, **kwargs)
        html_content = template.render(**context)
        message.attach(MIMEText(html_content, "html"))

        return message

    async def send_email(self, recipients: list[str], *args, **kwargs):
        """Send an email via an SMTP server."""
        message = self.generate_email(recipients, *args, **kwargs)
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_SENDER, recipients, message.as_string())


class AccountVerificationEmail(EmailGenerator):
    """Email sender for user registration verification."""

    def email_template(self) -> str:
        template_path = TEMPLATE_FOLDER / Path("account_verification.html")
        return template_path.read_text()

    def email_subject(self) -> str:
        return "Account Verification"

    def generate_verification_url(self, email: str) -> str:
        token = encode_url_safe_token({"email": email})
        return f"{settings.DOMAIN}/api/accounts/email-verification?token={token}"

    def email_context(self, *args, **kwargs) -> dict:
        verification_url = self.generate_verification_url(kwargs.get("email"))
        return {"user_name": kwargs.get("username"), "verification_url": verification_url}


class EmailSender:
    """Execute strategy from client."""

    def __init__(self, strategy: EmailGenerator):
        """Initialize."""
        self.strategy = strategy

    async def send(self, recipients: list[str], *args, **kwargs):
        """Delegate real strategy."""
        await self.strategy.send_email(recipients, *args, **kwargs)
