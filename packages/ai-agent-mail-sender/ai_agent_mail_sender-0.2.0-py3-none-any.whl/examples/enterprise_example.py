"""
Example demonstrating the enterprise features of the Mail Sender library.

This example showcases:
1. Async/concurrent support
2. Logging
3. Retry mechanism
4. Rate limiting
5. Template support
6. Connection pooling

Author: MD ZAID ANWAR
Email: zaidanwar26@gmail.com
"""

import os
import logging
import asyncio
from mail_sender import EmailSender

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Email configuration - replace with your own details
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "your-email@gmail.com"
# For Gmail, use an App Password:
# https://myaccount.google.com/security > App passwords
EMAIL_PASSWORD = "your-app-password"

# Test recipients - replace with real emails for testing
RECIPIENT_EMAILS = [
    "recipient1@example.com",
    "recipient2@example.com",
    "recipient3@example.com"
]

# Example 1: Basic sender with enterprise features
def example_sync_with_enterprise_features():
    """
    Example of using synchronous email with enterprise features like
    retry, logging, rate limiting, and template support.
    """
    print("\n=== Example 1: Sync Email with Enterprise Features ===")
    
    # Create email sender with enterprise features
    sender = EmailSender(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD,
        use_tls=True,
        log_level=logging.INFO,
        max_retries=3,
        retry_delay=2.0,
        rate_limit=10  # Limit to 10 emails per minute
    )
    
    # Send email with template
    try:
        # Prepare template context
        template_context = {
            "subject": "Enterprise Email Example",
            "content": "<p>This is a <strong>test email</strong> sent using the Mail Sender library with enterprise features.</p>",
            "action_url": "https://github.com/Brainstorm2605/email_sender",
            "action_text": "View Repository",
            "year": 2025,
            "company_name": "Mail Sender",
            "unsubscribe_url": "https://example.com/unsubscribe"
        }
        
        # Send email with retry logic (handled internally by the @with_retries decorator)
        success = sender.send_email(
            to_emails=RECIPIENT_EMAILS[0],
            subject="Enterprise Email Example",
            content="",  # Content will be from template
            is_html=True,
            template_name="basic_template.html",
            template_context=template_context
        )
        
        print(f"Email sent successfully: {success}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example 2: Async email sending with connection pooling
async def example_async_with_connection_pooling():
    """
    Example of using asynchronous email with connection pooling
    for high-throughput scenarios.
    """
    print("\n=== Example 2: Async Email with Connection Pooling ===")
    
    # Create email sender with connection pooling
    sender = EmailSender(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD,
        use_tls=True,
        log_level=logging.INFO,
        pool_connections=True,
        pool_size=3  # Keep up to 3 connections in the pool
    )
    
    # Send multiple emails asynchronously
    try:
        # Simple HTML content
        html_content = """
        <html>
          <body>
            <h1>Hello from Mail Sender</h1>
            <p>This is an <b>async email</b> sent with connection pooling.</p>
          </body>
        </html>
        """
        
        # Create and gather tasks for sending emails
        tasks = []
        for i in range(5):  # Send 5 emails
            tasks.append(
                sender.send_email_async(
                    to_emails=RECIPIENT_EMAILS[0],
                    subject=f"Async Email Example {i+1}",
                    content=html_content,
                    is_html=True
                )
            )
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        print(f"Emails sent: {sum(results)}/{len(results)} successful")
    except Exception as e:
        print(f"Error sending async emails: {e}")

# Example 3: Bulk email with rate limiting and concurrency control
async def example_bulk_email_with_rate_limit():
    """
    Example of sending bulk emails with rate limiting and concurrency control.
    """
    print("\n=== Example 3: Bulk Email with Rate Limiting ===")
    
    # Create email sender with rate limiting
    sender = EmailSender(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD,
        use_tls=True,
        log_level=logging.INFO,
        rate_limit=60,  # Limit to 60 emails per minute
        pool_connections=True
    )
    
    try:
        # Send bulk emails asynchronously with concurrency control
        results = await sender.send_bulk_email_async(
            to_emails=RECIPIENT_EMAILS,
            subject="Bulk Email Example",
            content="This is a test bulk email with rate limiting and concurrency control.",
            is_html=False,
            individual_emails=True,
            concurrency_limit=2  # Only send 2 emails concurrently
        )
        
        # Print results
        for email, success in results.items():
            print(f"Email to {email}: {'Success' if success else 'Failed'}")
            
        success_rate = sum(results.values()) / len(results) * 100
        print(f"Bulk email success rate: {success_rate:.1f}%")
    except Exception as e:
        print(f"Error sending bulk emails: {e}")

# Main async function to run all examples
async def main():
    print("=== Mail Sender Enterprise Examples ===")
    
    # Make sure templates directory exists
    templates_dir = os.path.join(os.path.dirname(__file__), "../mail_sender/templates")
    if not os.path.exists(templates_dir):
        print(f"Templates directory not found at: {templates_dir}")
        print("Make sure you have the templates directory set up correctly")
        return
    
    # Run the examples
    example_sync_with_enterprise_features()
    await example_async_with_connection_pooling()
    await example_bulk_email_with_rate_limit()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 