# Mail Sender

<div align="center">

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

**A secure and enterprise-grade email sender library for any workflow, including AI applications.**

</div>

## 📋 Overview

Mail Sender is a Python library that provides a simple yet powerful interface for sending emails securely. It's designed to be integrated into any workflow, with special consideration for AI applications.

## ✨ Features

- **🔒 Security-First Design**: Built with security as a top priority
- **📝 Flexible Content Support**: Send plain text or HTML emails
- **📎 File Attachments**: Easily attach files to your emails
- **📨 Bulk Email Support**: Send to multiple recipients with customizable time intervals
- **🧩 Zero External Dependencies**: Only requires aiosmtplib and jinja2 beyond the Python standard library
- **🤖 AI Ready**: Seamlessly integrates with AI workflows

### 🚀 Enterprise Features

- **⚡ Async Support**: Send emails asynchronously for non-blocking operation
- **📊 Comprehensive Logging**: Detailed logging for monitoring and debugging
- **🔄 Automatic Retry**: Built-in retry mechanism for handling transient errors
- **⏱️ Rate Limiting**: Control email sending rates to comply with provider limits
- **📄 Template System**: Jinja2 templates for beautiful, consistent email content
- **🔌 Connection Pooling**: Reuse connections for better performance in high-volume scenarios

## 📦 Installation

```bash
pip install ai-agent-mail-sender
```

## 🚀 Quick Start

```python
from mail_sender import EmailSender

# Initialize the email sender
sender = EmailSender(
    host="smtp.example.com",  # SMTP server host
    port=587,                 # SMTP server port
    username="your_email@example.com",
    password="your_password", 
    use_tls=True              # Default is True
)

# Send a simple email
success = sender.send_email(
    to_emails="recipient@example.com",
    subject="Hello from Mail Sender",
    content="This is a test email sent using the Mail Sender library.",
    is_html=False  # Default is False
)

if success:
    print("Email sent successfully!")
else:
    print("Failed to send email.")

# Send an HTML email with an attachment
html_content = """
<html>
  <body>
    <h1>Hello from Mail Sender</h1>
    <p>This is an <b>HTML</b> email sent using the Mail Sender library.</p>
    <p>This email includes a PDF attachment.</p>
  </body>
</html>
"""

sender.send_email(
    to_emails="recipient@example.com",
    subject="HTML Email with Attachment",
    content=html_content,
    attachments=["path/to/document.pdf"],
    is_html=True
)

# Send to multiple recipients with time intervals between emails
recipients = ["recipient1@example.com", "recipient2@example.com", "recipient3@example.com"]
results = sender.send_bulk_email(
    to_emails=recipients,
    subject="Bulk Email Test",
    content="This is a test email sent to multiple recipients.",
    attachments=["path/to/document.pdf"],  # Optional
    is_html=False,
    individual_emails=True,  # Send separate emails to each recipient
    interval=1.5,  # 1.5 minutes between emails
    randomize_interval=True  # Randomize the interval between 0 and 1.5 minutes
)

# Check results
for email, success in results.items():
    print(f"{email}: {'Success' if success else 'Failed'}")
```

## 🔍 Enterprise Examples

Check out the [examples directory](./examples) for detailed usage examples:

1. **Basic Example**: Simple text and HTML emails
2. **Advanced Example**: Attachments and bulk emailing with intervals
3. **AI Workflow Example**: Integration with AI-generated content
4. **Enterprise Example**: Demonstrates async, logging, retry, rate limiting, templates, and connection pooling

### Async Email Sending

```python
import asyncio
from mail_sender import EmailSender

async def send_emails():
    sender = EmailSender(
        host="smtp.example.com",
        port=587,
        username="your_email@example.com",
        password="your_password",
        use_tls=True,
        pool_connections=True  # Enable connection pooling
    )
    
    # Send an email asynchronously
    success = await sender.send_email_async(
        to_emails="recipient@example.com",
        subject="Async Email Example",
        content="This is an asynchronous email.",
        is_html=False
    )
    
    # Send bulk emails asynchronously with concurrency control
    results = await sender.send_bulk_email_async(
        to_emails=["recipient1@example.com", "recipient2@example.com"],
        subject="Async Bulk Email",
        content="This is a bulk async email.",
        individual_emails=True,
        concurrency_limit=5  # Limit concurrent sends
    )

# Run the async function
asyncio.run(send_emails())
```

### Template-Based Emails

```python
from mail_sender import EmailSender

sender = EmailSender(
    host="smtp.example.com",
    port=587,
    username="your_email@example.com",
    password="your_password"
)

# Send email using a template
sender.send_email(
    to_emails="recipient@example.com",
    subject="Template Email Example",
    content="",  # Content will come from the template
    template_name="basic_template.html",
    template_context={
        "subject": "Welcome to Our Service",
        "content": "<p>Thank you for signing up!</p>",
        "action_url": "https://example.com/dashboard",
        "action_text": "Go to Dashboard",
        "company_name": "Your Company"
    }
)
```

## 📚 API Reference

### EmailSender

```python
EmailSender(
    host, 
    port, 
    username, 
    password, 
    use_tls=True,
    log_level=logging.INFO,
    max_retries=3,
    retry_delay=1.0,
    rate_limit=None,
    pool_connections=False,
    pool_size=5
)
```

#### Parameters

- `host` (str): SMTP server host (e.g., smtp.gmail.com)
- `port` (int): SMTP server port (e.g., 587 for TLS, 465 for SSL)
- `username` (str): Email account username/email address
- `password` (str): Email account password or app password
- `use_tls` (bool, optional): Whether to use TLS encryption. Default is True.
- `log_level` (int, optional): Logging level from the logging module. Default is INFO.
- `max_retries` (int, optional): Maximum number of retry attempts for failed emails. Default is 3.
- `retry_delay` (float, optional): Delay between retry attempts in seconds. Default is 1.0.
- `rate_limit` (int, optional): Maximum number of emails per minute. Default is None (no limit).
- `pool_connections` (bool, optional): Whether to use connection pooling. Default is False.
- `pool_size` (int, optional): Maximum number of connections to keep in the pool. Default is 5.

### send_email

```python
send_email(
    to_emails, 
    subject, 
    content, 
    attachments=None, 
    is_html=False,
    template_name=None,
    template_context=None
)
```

#### Parameters

- `to_emails` (str or list): A single email address or a list of email addresses
- `subject` (str): Email subject
- `content` (str): Email content (plain text or HTML)
- `attachments` (list, optional): List of file paths to attach to the email
- `is_html` (bool, optional): Whether the content is HTML. Default is False.
- `template_name` (str, optional): Name of template file to use instead of content. Default is None.
- `template_context` (dict, optional): Context data for template rendering. Default is None.

#### Returns

- `bool`: True if email was sent successfully, False otherwise

### send_email_async

```python
async send_email_async(
    to_emails, 
    subject, 
    content, 
    attachments=None, 
    is_html=False,
    template_name=None,
    template_context=None
)
```

Asynchronous version of send_email with the same parameters and return value.

### send_bulk_email

```python
send_bulk_email(
    to_emails, 
    subject, 
    content, 
    attachments=None, 
    is_html=False, 
    individual_emails=False, 
    interval=None, 
    randomize_interval=False,
    template_name=None,
    template_context=None
)
```

#### Parameters

- `to_emails` (list): List of email addresses
- `subject` (str): Email subject
- `content` (str): Email content (plain text or HTML)
- `attachments` (list, optional): List of file paths to attach to the email
- `is_html` (bool, optional): Whether the content is HTML. Default is False.
- `individual_emails` (bool, optional): Whether to send individual emails to each recipient. Default is False.
- `interval` (float, optional): Time interval in minutes between emails (0-5 min). Default is None (no interval).
- `randomize_interval` (bool, optional): Whether to randomize the interval within the specified range. Default is False.
- `template_name` (str, optional): Name of template file to use instead of content. Default is None.
- `template_context` (dict, optional): Context data for template rendering. Default is None.

#### Returns

- `dict`: Results of the email sending with email addresses as keys and success status as values

### send_bulk_email_async

```python
async send_bulk_email_async(
    to_emails, 
    subject, 
    content, 
    attachments=None, 
    is_html=False, 
    individual_emails=False,
    concurrency_limit=5,
    template_name=None,
    template_context=None
)
```

#### Parameters

Same as send_bulk_email, with the addition of:
- `concurrency_limit` (int, optional): Maximum number of concurrent email sends. Default is 5.

#### Returns

- `dict`: Results of the email sending with email addresses as keys and success status as values

### render_template

```python
render_template(template_name, **context)
```

#### Parameters

- `template_name` (str): Name of the template file
- `**context`: Variables to pass to the template

#### Returns

- `str`: Rendered template content

## 🔐 Security Features

- Secure connections with TLS/SSL by default
- Protected password handling
- Secure file attachment processing
- SSL context with default security settings
- Automatic cleanup of sensitive information

## 📧 Common SMTP Server Settings

### Gmail
- Host: `smtp.gmail.com`
- Port: `587` (TLS) or `465` (SSL)
- Username: Your Gmail address
- Password: App password (if 2FA is enabled)
  - Go to your [Google Account Security settings](https://myaccount.google.com/security)
  - Enable 2-Step Verification if not already enabled
  - Go to "App passwords" and generate a new password for your app
  - Use this 16-character password in the library

### Outlook/Hotmail
- Host: `smtp.office365.com`
- Port: `587`
- Username: Your Outlook email address
- Password: Your password

### Yahoo Mail
- Host: `smtp.mail.yahoo.com`
- Port: `587` (TLS) or `465` (SSL)
- Username: Your Yahoo email address
- Password: App password (if 2FA is enabled)

### GoDaddy
- Host: `smtpout.secureserver.net`
- Port: `465` (SSL) or `587` (TLS)
- Username: Your full email address
- Password: Your email password

## 🏢 Enterprise Use Cases

- **Customer Communication**: Send personalized emails to customers
- **Reporting Systems**: Automatically email reports to stakeholders
- **AI Applications**: Send AI-generated insights and recommendations
- **Alert Systems**: Send critical alerts and notifications
- **Marketing Campaigns**: Manage email marketing campaigns with interval controls
- **High-Volume Applications**: Handle thousands of emails with connection pooling and rate limiting
- **Mission-Critical Systems**: Ensure delivery with retry mechanisms and detailed logging

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 👨‍💻 Author

**MD ZAID ANWAR**  
Email: zaidanwar26@gmail.com  
GitHub: [Brainstorm2605](https://github.com/Brainstorm2605)  
