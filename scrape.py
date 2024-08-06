import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# General Variables
smtp_server = "smtp.gmail.com"
smtp_port = 465  # or 587 for STARTTLS
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Verify the MongoDB URI
mongo_uri = os.getenv('MONGO_URI')

# Print the MongoDB URI for debugging
print(f"MONGO_URI: {mongo_uri}")