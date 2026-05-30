import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from langchain_core.tools import tool
from typing import Annotated

@tool
def send_email_tool(
    to_email: str,
    subject: str,
    body: str,
    file_name: str
):
    """
    Send an email with a file attachment.
    """

    try:
        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")

        # Create email
        message = MIMEMultipart()

        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject

        # Email body
        message.attach(MIMEText(body, "plain"))

        # Check file exists
        if not os.path.exists(file_name):
            return {
                "status": "error",
                "message": f"File '{file_name}' does not exist."
            }

        # Attach file
        with open(file_name, "rb") as attachment:

            part = MIMEBase("application", "octet-stream")

            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file_name)}"
        )

        message.attach(part)

        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()

            server.login(sender_email, sender_password)

            server.send_message(message)

        return {
            "status": "success",
            "message": f"Email with attachment sent to {to_email}"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

@tool
def write_file_tool(file_name: str, content: str):
    """
    Create a new file or append content to an existing file.
    """

    print("WRITER NODE EXECUTED")
    

    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(content + "\n")
        print(f"file {file_name} saved successfully!")
        return {
            "status": "success",
            "message": f"Content saved successfully in {file_name}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@tool
def read_file_tool(
    file_name: str,
    end: Annotated[int, "Line number to read until"],
    start: Annotated[int, "Line number to start reading from"] = 0
):
    """
    Read content from an existing file.
    """

    print("READ NODE EXECUTED")

    try:
        if not os.path.exists(file_name):
            return {
                "status": "error",
                "message": f"File '{file_name}' does not exist.",
                "content": []
            }

        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()

        content = lines[start:end]

        return {
            "status": "success",
            "message": f"File {file_name} read successfully",
            "content": content
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "content": []
        }


@tool
def edit_file_tool(
    content: Annotated[str, "Content to replace existing lines with"],
    file_name: str,
    end: Annotated[int, "Ending line number"],
    start: Annotated[int, "Starting line number"] = 0
):
    """
    Edit specific lines in an existing file.
    """

    print("EDIT NODE EXECUTED")

    try:
        if not os.path.exists(file_name):
            
            return {
                "status": "error",
                "message": f"File '{file_name}' does not exist."
            }

        with open(file_name, "r", encoding="utf-8") as file:
            file_data = file.readlines()

        # Ensure newline
        replacement = content + "\n"

        updated_data = (
            file_data[:start]
            + [replacement]
            + file_data[end:]
        )

        with open(file_name, "w", encoding="utf-8") as file:
            file.writelines(updated_data)
        
        print(f"file {file_name} edited and saved successfully!")
        return {
            "status": "success",
            "message": f"Content edited successfully in {file_name}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


writer_tools = [write_file_tool, read_file_tool, edit_file_tool,send_email_tool]