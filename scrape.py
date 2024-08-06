import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pymongo import MongoClient

# General Variables
smtp_server = "smtp.gmail.com"
smtp_port = 465  # or 587 for STARTTLS
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email sending function
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

# MongoDB connection
def connect_to_mongo(uri):
    """Connect to MongoDB and return the client."""
    client = MongoClient(uri)
    return client

def read_documents(client, db_name, collection_name, filter, limit=None):
    """Read documents from a specified MongoDB collection with optional limit."""
    db = client[db_name]
    collection = db[collection_name]
    query = collection.find(filter)
    
    if limit:
        query = query.limit(limit)
    return list(query)

# MongoDB connection string
mongo_uri = os.getenv('MONGO_URI')
print(mongo_uri)
# Connect to MongoDB
client = connect_to_mongo(mongo_uri)

# Example usage: Read the first 60 documents
filter = {'status': 'Not Sent'}
documents = read_documents(client, 'jobs', 'jobsUrls', filter, limit=60)

# If there are no emails, notify by emailing me
print(len(documents))
if len(documents) != 60:
    sender_email = "abdellahgram01@gmail.com"
    receiver_email = "abdolahwidadi00@gmail.com"
    subject = "Reminder: Add Email to the Database"
    body = "Dear ME,\n\nPlease add the following email address to the database as it is currently empty:\n\nRun the webscraping script in your notebook as soon as possible to not miss the upcoming opportunities.\n\nThank you\n\nAbdellah."
    
    # Send remainder
    send_email_with_attachment(sender_email, receiver_email, subject, body, "emailNotFound.png",
                               smtp_server, smtp_port, smtp_username, smtp_password)
else:
    for d in documents:
        # Send 60 emails at once
        sender_email = "abdellahgram01@gmail.com"
        receiver_email = "abdolahwidadi00@gmail.com"  # [d['Email']]
        subject = f"Application for {d['Email']} Position"
        body = f"""Dear Hiring manager,

I am excited to apply for the {d['Job_Title']} position at your company. With a strong background in software development, a passion for coding, and a commitment to continuous learning, I am eager to contribute to your team and help drive the success of your projects.

Background and Experience:

I hold a bachelor's degree in Business Intelligence and Statistics and have gained extensive experience in software development through various projects and internships. My key skills include:

Programming Languages: Proficient in Python, Java, JavaScript, and other programming languages.
Web Development: Experienced in HTML, CSS, and JavaScript frameworks like React.js and Angular.
Data Analysis: Skilled in SQL, NoSQL, and data visualization tools such as Tableau and Power BI.
System Programming: Competent in system-level programming and optimizing performance in Linux environments.
Problem-Solving: Strong analytical and problem-solving abilities, demonstrated through successful project completions and enhancements.
Key Achievements:

In my previous roles, I have consistently delivered high-quality solutions that meet user needs and business objectives. For example, I developed a real-time statistical application during my internship at the Chambre de Commerce, d'Industrie et de Services Agadir, which improved client satisfaction and reduced project delivery time.

Why your company?

I am particularly drawn to your company because of its innovative approach and commitment to excellence. The opportunity to work on challenging and impactful projects, collaborate with talented professionals, and contribute to your company’s mission is very appealing to me.

Skills and Qualifications:

Degree in Computer Science
Proficiency in multiple programming languages and web technologies
Experience with data analysis and visualization tools
Strong problem-solving and analytical skills
Excellent communication and teamwork abilities
Attached is my resume for your review. I look forward to the opportunity to discuss how my skills and experiences align with the goals of your company. Thank you for considering my application.

Best regards,

Gram Abdellah
+212 642 715 170
abdellahgram01@gmail.com
https://www.linkedin.com/in/abdegram0213/"""
        attachment_path = "Updated resume Data Entry Clerk.pdf"
        try:
            send_email_with_attachment(sender_email, receiver_email, subject, body, attachment_path, smtp_server, smtp_port, smtp_username, smtp_password)
            # collection.delete_one({'_id': d['_id']})
        except Exception as e:
            print(f"Error: The email failed to send. {str(e)}")
        
        break
