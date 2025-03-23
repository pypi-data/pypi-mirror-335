"""
Basic example demonstrating how to use the mail_sender library.
"""

from mail_sender import EmailSender

def main():
    # Replace these with your actual SMTP server details
    host = "smtp.example.com"
    port = 587
    username = "your_email@example.com"
    password = "your_password"
    
    print("Mail Sender Basic Example")
    print("========================")
    
    # Initialize the email sender
    sender = EmailSender(
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=True
    )
    
    # Recipient email
    recipient = "recipient@example.com"
    
    # Send a plain text email
    print("\nSending plain text email...")
    success = sender.send_email(
        to_emails=recipient,
        subject="Test Plain Text Email",
        content="Hello! This is a test email sent using the mail_sender library.",
        is_html=False
    )
    
    if success:
        print("✓ Plain text email sent successfully!")
    else:
        print("✗ Failed to send plain text email.")
    
    # Send an HTML email
    print("\nSending HTML email...")
    html_content = """
    <html>
      <body>
        <h1 style="color: #2a76dd;">Hello from Mail Sender!</h1>
        <p>This is an <b>HTML</b> email sent using the mail_sender library.</p>
        <p>Features:</p>
        <ul>
          <li>Support for <i>HTML formatting</i></li>
          <li>Easy to use API</li>
          <li>Secure by default</li>
        </ul>
      </body>
    </html>
    """
    
    success = sender.send_email(
        to_emails=recipient,
        subject="Test HTML Email",
        content=html_content,
        is_html=True
    )
    
    if success:
        print("✓ HTML email sent successfully!")
    else:
        print("✗ Failed to send HTML email.")
    
    print("\nExample completed.")

if __name__ == "__main__":
    main() 