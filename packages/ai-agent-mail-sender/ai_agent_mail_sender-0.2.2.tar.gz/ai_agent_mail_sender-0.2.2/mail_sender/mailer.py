"""
Secure email sender library for use in any workflow, including AI applications.

This module provides a secure and reliable way to send emails with support for:
- Plain text and HTML content
- File attachments
- Bulk sending with customizable intervals
- TLS/SSL encryption
- Async support
- Logging and retry mechanisms
- Template rendering

Author: MD ZAID ANWAR
Email: zaidanwar26@gmail.com
Repository: https://github.com/Brainstorm2605/email_sender
"""

import smtplib
import ssl
import os
import time
import random
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Union, Dict, Any, Callable
import aiosmtplib
import jinja2
from functools import wraps
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class EmailSender:
    """
    A secure email sender class that can be used to send emails in any workflow.
    
    Required parameters:
    - host: SMTP server host
    - port: SMTP server port
    - username: Email account username
    - password: Email account password
    
    Optional parameters:
    - use_tls: Whether to use TLS encryption. If not specified, will auto-detect based on port.
      - Port 465: Will use SSL (use_tls=False)
      - Port 587: Will use STARTTLS (use_tls=True)
      - Other ports: Uses provided value or defaults to True
    - log_level: Logging level (default: INFO)
    - max_retries: Maximum number of retry attempts for failed emails (default: 3)
    - retry_delay: Delay between retry attempts in seconds (default: 1)
    - rate_limit: Maximum number of emails per minute (default: None)
    - pool_connections: Whether to use connection pooling (default: False)
    - pool_size: Maximum number of connections to keep in the pool (default: 5)
    """
    
    def __init__(
        self, 
        host: str, 
        port: int, 
        username: str, 
        password: str, 
        use_tls: Optional[bool] = None,
        log_level: int = logging.INFO,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit: Optional[int] = None,
        pool_connections: bool = False,
        pool_size: int = 5
    ):
        """Initialize the EmailSender with SMTP server details."""
        self.host = host
        self.port = port
        self.username = username
        self._password = password  # Using underscore to indicate it's a protected attribute
        
        # Auto-detect the appropriate security protocol based on the port
        if use_tls is None:
            if port == 465:
                # Port 465 uses SSL, not explicit TLS
                self.use_tls = False
                logger.info(f"Auto-detected SSL mode for port {port}")
            elif port == 587:
                # Port 587 uses explicit TLS (STARTTLS)
                self.use_tls = True
                logger.info(f"Auto-detected TLS (STARTTLS) mode for port {port}")
            else:
                # Default to TLS for other ports
                self.use_tls = True
                logger.info(f"Using default TLS setting for port {port}")
        else:
            self.use_tls = use_tls
            # Add a warning if the user explicitly sets a protocol that doesn't match the standard for the port
            if (port == 465 and use_tls) or (port == 587 and not use_tls):
                logger.warning(
                    f"Non-standard protocol configuration: port {port} with use_tls={use_tls}. "
                    f"Typically, port 465 uses SSL (use_tls=False) and port 587 uses STARTTLS (use_tls=True)."
                )
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        self.pool_connections = pool_connections
        self.pool_size = pool_size
        
        # Set up logging
        self._setup_logging(log_level)
        
        # Connection pool
        self._connection_pool = []
        self._pool_lock = asyncio.Lock() if pool_connections else None
        
        # Rate limiting
        self._sent_timestamps = []
        
        # Template environment
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        if not os.path.exists(template_dir):
            template_dir = "templates"  # Fallback to local templates directory
        
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"EmailSender initialized with host={host}, port={port}, use_tls={self.use_tls}")
    
    def _setup_logging(self, log_level: int) -> None:
        """
        Set up logging configuration.
        
        Args:
            log_level: The logging level to use
        """
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        logger.setLevel(log_level)
        
    def _create_message(
        self, 
        to_emails: Union[str, List[str]], 
        subject: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = False
    ) -> MIMEMultipart:
        """
        Create an email message with optional attachments.
        
        Args:
            to_emails: A single email address or a list of email addresses
            subject: Email subject
            content: Email content (plain text or HTML)
            attachments: List of file paths to attach
            is_html: Whether the content is HTML
            
        Returns:
            MIMEMultipart: The email message object
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.username
        
        # Handle single email or list of emails
        if isinstance(to_emails, str):
            message["To"] = to_emails
        else:
            message["To"] = ", ".join(to_emails)
            
        # Set the content type based on whether it's HTML or plain text
        content_type = "html" if is_html else "plain"
        message.attach(MIMEText(content, content_type))
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                self._add_attachment(message, file_path)
        
        return message
    
    def _add_attachment(self, message: MIMEMultipart, file_path: str) -> None:
        """
        Add an attachment to the email message.
        
        Args:
            message: The email message object
            file_path: Path to the file to attach
        """
        if not os.path.isfile(file_path):
            logger.error(f"Attachment file not found: {file_path}")
            raise FileNotFoundError(f"Attachment file not found: {file_path}")
            
        # Get the filename from the path
        filename = os.path.basename(file_path)
        
        try:
            # Determine the attachment type
            if file_path.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
                # For document files
                with open(file_path, 'rb') as file:
                    attachment = MIMEApplication(file.read(), _subtype=os.path.splitext(file_path)[1][1:])
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            else:
                # For other file types
                with open(file_path, 'rb') as file:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(file.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            
            # Add the attachment to the message
            message.attach(attachment)
            logger.debug(f"Added attachment: {filename}")
        except Exception as e:
            logger.error(f"Error attaching file {filename}: {str(e)}")
            raise Exception(f"Error attaching file {filename}: {str(e)}")
    
    def _check_rate_limit(self) -> None:
        """
        Check if the rate limit has been reached.
        Raises RuntimeError if the rate limit is exceeded.
        """
        if not self.rate_limit:
            return
            
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self._sent_timestamps = [ts for ts in self._sent_timestamps if now - ts < timedelta(minutes=1)]
        
        # Check if we've hit the rate limit
        if len(self._sent_timestamps) >= self.rate_limit:
            logger.warning(f"Rate limit of {self.rate_limit} emails per minute exceeded")
            raise RuntimeError(f"Rate limit of {self.rate_limit} emails per minute exceeded")
        
        # Add current timestamp
        self._sent_timestamps.append(now)
    
    def with_retries(max_retries=3, retry_delay=1.0):
        """
        Decorator for functions that need retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Callable: Decorated function
        """
        def decorator(func):
            @wraps(func)
            def sync_wrapper(self, *args, **kwargs):
                retries = kwargs.pop('max_retries', self.max_retries)
                delay = kwargs.pop('retry_delay', self.retry_delay)
                
                for attempt in range(retries + 1):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        if attempt < retries:
                            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                            time.sleep(delay)
                            # Increase delay for next attempt
                            delay *= 2
                        else:
                            logger.error(f"All {retries + 1} attempts failed. Last error: {str(e)}")
                            raise
            
            @wraps(func)
            async def async_wrapper(self, *args, **kwargs):
                retries = kwargs.pop('max_retries', self.max_retries)
                delay = kwargs.pop('retry_delay', self.retry_delay)
                
                for attempt in range(retries + 1):
                    try:
                        return await func(self, *args, **kwargs)
                    except Exception as e:
                        if attempt < retries:
                            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                            await asyncio.sleep(delay)
                            # Increase delay for next attempt
                            delay *= 2
                        else:
                            logger.error(f"All {retries + 1} attempts failed. Last error: {str(e)}")
                            raise
            
            # Choose the appropriate wrapper based on whether the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    async def _get_connection_from_pool(self):
        """
        Get a connection from the pool or create a new one if the pool is empty.
        
        Returns:
            Connection: SMTP connection object
        """
        if not self.pool_connections:
            return None
            
        async with self._pool_lock:
            if self._connection_pool:
                conn = self._connection_pool.pop()
                logger.debug("Reusing connection from pool")
                return conn
            
        logger.debug("Creating new connection for pool")
        conn = await self._create_new_connection()
        return conn
    
    async def _return_connection_to_pool(self, conn):
        """
        Return a connection to the pool if pool_connections is enabled and the pool is not full.
        
        Args:
            conn: The connection to return to the pool
        """
        if not self.pool_connections:
            try:
                await conn.quit()
            except:
                pass
            return
            
        async with self._pool_lock:
            if len(self._connection_pool) < self.pool_size:
                self._connection_pool.append(conn)
                logger.debug("Returned connection to pool")
            else:
                try:
                    await conn.quit()
                    logger.debug("Pool full, connection closed")
                except:
                    pass
    
    async def _create_new_connection(self):
        """
        Create a new SMTP connection.
        
        Returns:
            Connection: SMTP connection object
        """
        context = ssl.create_default_context()
        
        if self.use_tls:
            client = aiosmtplib.SMTP(hostname=self.host, port=self.port, use_tls=False)
            await client.connect()
            await client.starttls(validate_certs=True, client_cert=None, cert_verify_callback=None)
        else:
            client = aiosmtplib.SMTP_SSL(hostname=self.host, port=self.port, ssl_context=context)
            await client.connect()
            
        await client.login(self.username, self._password)
        return client
    
    def render_template(self, template_name: str, **context) -> str:
        """
        Render a Jinja2 template with the provided context.
        
        Args:
            template_name: Name of the template file
            **context: Variables to pass to the template
            
        Returns:
            str: Rendered template content
        """
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise ValueError(f"Error rendering template {template_name}: {str(e)}")
    
    @with_retries()
    def send_email(
        self, 
        to_emails: Union[str, List[str]], 
        subject: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        template_name: Optional[str] = None,
        template_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an email to one or more recipients.
        
        Args:
            to_emails: A single email address or a list of email addresses
            subject: Email subject
            content: Email content (plain text or HTML)
            attachments: List of file paths to attach
            is_html: Whether the content is HTML (default: False)
            template_name: Name of template file to use instead of content (default: None)
            template_context: Context data for template rendering (default: None)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending email to {to_emails}")
            
            # Check rate limit
            self._check_rate_limit()
            
            # Handle template rendering if provided
            if template_name:
                if not template_context:
                    template_context = {}
                content = self.render_template(template_name, **template_context)
                is_html = True
            
            # Create the email message
            message = self._create_message(to_emails, subject, content, attachments, is_html)
            
            # Create secure connection with the server
            context = ssl.create_default_context()
            
            # Send email
            if self.use_tls:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls(context=context)
                    server.login(self.username, self._password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                    server.login(self.username, self._password)
                    server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    @with_retries()        
    async def send_email_async(
        self, 
        to_emails: Union[str, List[str]], 
        subject: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        template_name: Optional[str] = None,
        template_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an email asynchronously to one or more recipients.
        
        Args:
            to_emails: A single email address or a list of email addresses
            subject: Email subject
            content: Email content (plain text or HTML)
            attachments: List of file paths to attach
            is_html: Whether the content is HTML (default: False)
            template_name: Name of template file to use instead of content (default: None)
            template_context: Context data for template rendering (default: None)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending async email to {to_emails}")
            
            # Check rate limit
            self._check_rate_limit()
            
            # Handle template rendering if provided
            if template_name:
                if not template_context:
                    template_context = {}
                content = self.render_template(template_name, **template_context)
                is_html = True
            
            # Create the email message
            message = self._create_message(to_emails, subject, content, attachments, is_html)
            
            # Get connection (from pool if enabled)
            client = await self._get_connection_from_pool() or await self._create_new_connection()
            
            try:
                # Send the message
                await client.send_message(message)
                logger.info(f"Async email sent successfully to {to_emails}")
                
                # Return connection to pool
                await self._return_connection_to_pool(client)
                return True
            except Exception as e:
                # Try to close the connection on error
                try:
                    await client.quit()
                except:
                    pass
                raise
                
        except Exception as e:
            logger.error(f"Error sending async email: {e}")
            raise
            
    @with_retries()
    def send_bulk_email(
        self, 
        to_emails: List[str], 
        subject: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        individual_emails: bool = False,
        interval: Optional[float] = None,
        randomize_interval: bool = False,
        template_name: Optional[str] = None,
        template_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send emails to multiple recipients with optional interval between sends.
        
        Args:
            to_emails: List of email addresses
            subject: Email subject
            content: Email content (plain text or HTML)
            attachments: List of file paths to attach
            is_html: Whether the content is HTML (default: False)
            individual_emails: Whether to send individual emails to each recipient (default: False)
            interval: Time interval in minutes between emails (0-5 min, default: None)
            randomize_interval: Whether to randomize the interval within the specified range (default: False)
            template_name: Name of template file to use instead of content (default: None)
            template_context: Context data for template rendering (default: None)
            
        Returns:
            dict: Results of the email sending with email addresses as keys and success status as values
        """
        logger.info(f"Starting bulk email to {len(to_emails)} recipients")
        results = {}
        
        # Validate interval
        if interval is not None:
            if not 0 <= interval <= 5:
                error_msg = "Interval must be between 0 and 5 minutes"
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Convert minutes to seconds
            interval_seconds = interval * 60
        
        # Handle template rendering if provided
        if template_name:
            if not template_context:
                template_context = {}
            content = self.render_template(template_name, **template_context)
            is_html = True
        
        # Send as individual emails
        if individual_emails:
            for i, email in enumerate(to_emails):
                try:
                    # Check rate limit
                    self._check_rate_limit()
                    
                    # Send email
                    results[email] = self.send_email(
                        email, subject, content, attachments, is_html
                    )
                    
                    # Add delay if not the last email and interval is specified
                    if i < len(to_emails) - 1 and interval is not None:
                        delay = interval_seconds
                        if randomize_interval:
                            # Randomize between 0 and specified interval
                            delay = random.uniform(0, interval_seconds)
                        time.sleep(delay)
                except Exception as e:
                    logger.error(f"Error sending bulk email to {email}: {e}")
                    results[email] = False
        # Send as one email with multiple recipients
        else:
            try:
                # Check rate limit
                self._check_rate_limit()
                
                success = self.send_email(to_emails, subject, content, attachments, is_html)
                for email in to_emails:
                    results[email] = success
            except Exception as e:
                logger.error(f"Error sending bulk email: {e}")
                for email in to_emails:
                    results[email] = False
        
        logger.info(f"Bulk email completed. Success rate: {sum(results.values())}/{len(results)}")            
        return results
    
    async def send_bulk_email_async(
        self, 
        to_emails: List[str], 
        subject: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        individual_emails: bool = False,
        concurrency_limit: int = 5,
        template_name: Optional[str] = None,
        template_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send emails asynchronously to multiple recipients with concurrency control.
        
        Args:
            to_emails: List of email addresses
            subject: Email subject
            content: Email content (plain text or HTML)
            attachments: List of file paths to attach
            is_html: Whether the content is HTML (default: False)
            individual_emails: Whether to send individual emails to each recipient (default: False)
            concurrency_limit: Maximum number of concurrent email sends (default: 5)
            template_name: Name of template file to use instead of content (default: None)
            template_context: Context data for template rendering (default: None)
            
        Returns:
            dict: Results of the email sending with email addresses as keys and success status as values
        """
        logger.info(f"Starting async bulk email to {len(to_emails)} recipients")
        results = {}
        
        # Handle template rendering if provided
        if template_name:
            if not template_context:
                template_context = {}
            content = self.render_template(template_name, **template_context)
            is_html = True
        
        # Send as individual emails with concurrency control
        if individual_emails:
            # Create a semaphore to limit concurrency
            sem = asyncio.Semaphore(concurrency_limit)
            
            async def send_one(email):
                async with sem:
                    try:
                        return await self.send_email_async(
                            email, subject, content, attachments, is_html
                        )
                    except Exception as e:
                        logger.error(f"Error sending async bulk email to {email}: {e}")
                        return False
            
            # Create and gather tasks
            tasks = [send_one(email) for email in to_emails]
            results_list = await asyncio.gather(*tasks)
            
            # Map results to emails
            for email, result in zip(to_emails, results_list):
                results[email] = result
        # Send as one email with multiple recipients
        else:
            try:
                success = await self.send_email_async(to_emails, subject, content, attachments, is_html)
                for email in to_emails:
                    results[email] = success
            except Exception as e:
                logger.error(f"Error sending async bulk email: {e}")
                for email in to_emails:
                    results[email] = False
        
        logger.info(f"Async bulk email completed. Success rate: {sum(results.values())}/{len(results)}")            
        return results 