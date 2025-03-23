"""
Example of using mail_sender in an AI workflow.

This example demonstrates how to integrate the mail_sender library
in an AI-powered script that generates content and sends emails.
"""

import os
import time
from mail_sender import EmailSender
from datetime import datetime

# Simulated AI function (in real scenarios, this would use an actual AI model)
def ai_generate_content(user_data):
    """Simulates AI-generated content based on user data."""
    name = user_data.get("name", "User")
    interests = user_data.get("interests", [])
    
    # In a real scenario, this would call an AI API
    greeting = f"Hello {name},"
    
    if interests:
        content = f"Based on your interests in {', '.join(interests)}, we thought you might like:\n\n"
        for interest in interests:
            content += f"- New information about {interest}\n"
            content += f"- Recommended resources for {interest}\n"
    else:
        content = "Here are some general recommendations for you:\n\n"
        content += "- Latest industry updates\n"
        content += "- Popular resources in your field\n"
    
    closing = f"\nBest regards,\nYour AI Assistant\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return {
        "subject": f"Personalized Recommendations for {name}",
        "content": f"{greeting}\n\n{content}\n{closing}",
        "html_content": f"""
        <html>
          <body>
            <p>{greeting}</p>
            <p>{content.replace('\n', '<br>')}</p>
            <p>{closing.replace('\n', '<br>')}</p>
          </body>
        </html>
        """
    }

def send_ai_generated_emails(email_config, users_data, use_html=True, add_attachment=False):
    """Sends AI-generated emails based on user data."""
    print(f"Initializing email sender with {email_config['host']}...")
    
    # Initialize the EmailSender
    sender = EmailSender(
        host=email_config['host'],
        port=email_config['port'],
        username=email_config['username'],
        password=email_config['password'],
        use_tls=email_config.get('use_tls', True)
    )
    
    # Create a simple attachment if needed
    attachment_path = None
    if add_attachment:
        attachment_path = "ai_generated_report.txt"
        with open(attachment_path, "w") as f:
            f.write("This is an AI-generated report\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Contains personalized recommendations based on user interests.")
    
    # Process each user
    results = {}
    for i, user in enumerate(users_data):
        print(f"Processing user {i+1}/{len(users_data)}: {user['name']} ({user['email']})")
        
        # AI generates personalized content
        ai_content = ai_generate_content(user)
        
        # Send email with AI-generated content
        if use_html:
            content = ai_content["html_content"]
        else:
            content = ai_content["content"]
        
        # Prepare attachments list if needed
        attachments = [attachment_path] if attachment_path else None
        
        # Send email
        print(f"Sending personalized email to {user['email']}...")
        success = sender.send_email(
            to_emails=user['email'],
            subject=ai_content["subject"],
            content=content,
            attachments=attachments,
            is_html=use_html
        )
        
        results[user['email']] = success
        if success:
            print(f"✓ Email sent successfully to {user['email']}")
        else:
            print(f"✗ Failed to send email to {user['email']}")
        
        # Add a small delay between emails
        if i < len(users_data) - 1:
            time.sleep(1)
    
    # Clean up the attachment file if it was created
    if attachment_path and os.path.exists(attachment_path):
        os.remove(attachment_path)
        print(f"Removed temporary file: {attachment_path}")
    
    return results

def main():
    """Main function demonstrating the AI workflow."""
    print("AI Workflow Email Example")
    print("========================")
    
    # Example email configuration
    email_config = {
        'host': "smtp.example.com",
        'port': 587,
        'username': "your_email@example.com",
        'password': "your_password",
        'use_tls': True
    }
    
    # Sample user data - in a real scenario, this would come from a database
    users_data = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "interests": ["AI", "Machine Learning", "Python"]
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "interests": ["Data Science", "Visualization", "Statistics"]
        }
    ]
    
    # Send AI-generated emails to users
    results = send_ai_generated_emails(
        email_config=email_config,
        users_data=users_data,
        use_html=True,  # Use HTML formatting
        add_attachment=True  # Add a simple attachment
    )
    
    # Print summary
    print("\nEmail Sending Summary:")
    success_count = sum(1 for success in results.values() if success)
    print(f"Successfully sent: {success_count}/{len(results)}")
    print(f"Failed: {len(results) - success_count}/{len(results)}")
    
    print("\nAI workflow completed!")

if __name__ == "__main__":
    main() 