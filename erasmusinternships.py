import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pymongo import MongoClient
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
# General Variables
smtp_server = "smtp.gmail.com"
smtp_port = 465  # or 587 for STARTTLS
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Verify the MongoDB URI
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri.startswith('mongodb://') and not mongo_uri.startswith('mongodb+srv://'):
    raise ValueError("Invalid MongoDB URI. It must start with 'mongodb://' or 'mongodb+srv://'")

# MongoDB connection
def connect_to_mongo(uri):
    """Connect to MongoDB and return the client."""
    try:
        client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
        client.admin.command('ping')  # Ping to test connection
        return client
    except ServerSelectionTimeoutError as err:
        print(f"Server selection error: {err}")
        raise


def read_documents(client, db_name, collection_name, filter, limit=None):
    """Read documents from a specified MongoDB collection with optional limit."""
    db = client[db_name]
    collection = db[collection_name]
    query = collection.find(filter)
    
    if limit:
        query = query.limit(limit)
    return list(query)

def read_collection(client, db_name, collection_name):
    db = client[db_name]
    collection = db[collection_name]
    return collection

#Email sending df
def send_email_with_attachment(sender_email, receiver_emails, subject, body, attachment_path, smtp_server, smtp_port, smtp_username, smtp_password):
    # Ensure receiver_emails is a list
    if isinstance(receiver_emails, str):
        receiver_emails = receiver_emails.split(", ")

    # Create the email header
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = subject


    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    if os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)
    else:
        print(f"Attachment path '{attachment_path}' does not exist.")
        return

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_emails, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")


# Connect to MongoDB
client = connect_to_mongo(mongo_uri)

# Example usage: Read the first 60 documents
filter={'isEmail': 'true','isSent':'Not Sent'}
documents = read_documents(client, 'erasmusinternships', 'jobsUrls', filter, limit=60)
collection = read_collection(client, 'erasmusinternships', 'jobsUrls')

# If there are no emails, notify by emailing me
print(len(documents))
if len(documents) >= 4:
    for d in documents:
        # Send 60 emails at once
        sender_email = "abdellahgram01@gmail.com"
        receiver_email = d['Email']
        print(d)
        subject = f"Inquiry Regarding Erasmus Internship Application"
        # Function to read file content
        def read_file(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        # Read the email templates
        body_intern_template = read_file('internships.txt')
        body =body_intern_template.format(Job_Title=d['title'])


        attachment_path = "Updated resume Data Entry Clerk.pdf"
        try:
            print(f"Sending ... ! ")
            send_email_with_attachment(sender_email, receiver_email, subject, body, attachment_path, smtp_server, smtp_port, smtp_username, smtp_password)
            collection.update_one({'_id': d['_id']} , {'$set': {'isSent': 'Sent'}})
            # collection.delete_one({'_id': d['_id']})
        except Exception as e:
            print(f"Error: The email failed to send. {str(e)}")
