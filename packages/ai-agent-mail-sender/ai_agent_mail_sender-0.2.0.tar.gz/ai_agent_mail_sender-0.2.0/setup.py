from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai_agent_mail_sender",
    version="0.2.0",
    author="MD ZAID ANWAR",
    author_email="zaidanwar26@gmail.com",
    description="A secure and enterprise-grade email sender library for any workflow, including AI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Brainstorm2605/email_sender",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiosmtplib>=2.0.0",
        "jinja2>=3.0.0",
    ],
    keywords=["email", "smtp", "mail", "sender", "async", "enterprise", "secure"],
    package_data={
        "mail_sender": ["templates/*.html"],
    },
    include_package_data=True,
) 