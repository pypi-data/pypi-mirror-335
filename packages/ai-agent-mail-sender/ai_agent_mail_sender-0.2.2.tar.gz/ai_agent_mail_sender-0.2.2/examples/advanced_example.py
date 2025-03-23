"""
Advanced example demonstrating attachments and bulk emailing with the mail_sender library.
"""

from mail_sender import EmailSender
import time
import os

def create_sample_attachment(filename="sample_attachment.txt"):
    """Create a sample attachment file for demonstration."""
    with open(filename, "w") as f:
        f.write("This is a sample attachment file.\n")
        f.write(f"Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return filename

def main():
    # Replace these with your actual SMTP server details
    host = "smtp.example.com"
    port = 587
    username = "your_email@example.com"
    password = "your_password"
    
    print("Mail Sender Advanced Example")
    print("===========================")
    
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
    
    # Create a sample attachment
    attachment_path = create_sample_attachment()
    print(f"Created sample attachment: {attachment_path}")
    
    # Send an email with attachment
    print("\nSending email with attachment...")
    html_with_attachment = """
    <html>
      <body>
        <h1 style="color: #e91e63;">Email with Attachment</h1>
        <p>This is an <b>HTML</b> email with a text file attachment.</p>
        <p>The attachment was created at: {}</p>
      </body>
    </html>
    """.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    
    success = sender.send_email(
        to_emails=recipient,
        subject="Test Email with Attachment",
        content=html_with_attachment,
        attachments=[attachment_path],
        is_html=True
    )
    
    if success:
        print("✓ Email with attachment sent successfully!")
    else:
        print("✗ Failed to send email with attachment.")
    
    # Send bulk email with time intervals
    print("\nSending bulk email with time intervals...")
    recipients = [
        "recipient1@example.com",
        "recipient2@example.com",
        "recipient3@example.com"
    ]
    
    results = sender.send_bulk_email(
        to_emails=recipients,
        subject="Bulk Email Test - With Intervals",
        content="This is a test email sent to multiple recipients with time intervals.",
        attachments=[attachment_path],
        is_html=False,
        individual_emails=True,
        interval=0.5,  # 30 seconds between emails
        randomize_interval=True  # Randomize the interval
    )
    
    # Check results
    print("\nBulk email results:")
    for email, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"{email}: {status}")
    
    # Clean up the attachment file
    try:
        os.remove(attachment_path)
        print(f"\nCleanup: Removed {attachment_path}")
    except:
        pass
    
    print("\nExample completed.")

if __name__ == "__main__":
    main() 