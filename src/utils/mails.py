from abc import ABC, abstractmethod


class EmailGenerator(ABC):
    @abstractmethod
    def get_email_template(self) -> str:
        """Return the email template file."""

    @abstractmethod
    def get_email_subject(self) -> str:
        """Abstract method to define email subject."""
        pass

    @abstractmethod
    def get_email_context(self, recipients: list[str]) -> dict:
        """Abstract method to generate email context."""
        pass

    async def send_html_email(self, recipients: list[str]):
        """Deliver an email with the specified subject and template."""
        pass


class AccountVerificationEmail(EmailGenerator):
    """Email sender for user registration verification."""

    def get_email_template(self) -> str:
        pass

    def get_email_subject(self) -> str:
        pass

    def get_email_context(self, recipients: list[str]) -> dict:
        pass


class EmailSender:
    """Execute strategy from client."""

    def __init__(self, strategy: EmailGenerator):
        """Initialize."""
        self.strategy = strategy

    async def send(self, recipients: list[str]):
        """Delegate real strategy."""
        await self.strategy.send_html_email(recipients)
