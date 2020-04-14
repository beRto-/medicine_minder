import smtplib
import email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def connect_to_gmail_smtp():
    SERVER = "smtp.gmail.com"
    myGmail = "example_from_user@gmail.com"
    myGMPasswd = "password_goes_here"

    server = smtplib.SMTP(SERVER, 587)
    server.ehlo()
    server.starttls()
    server.login(myGmail, myGMPasswd)
    return server


def disconnect_from_gmail_smtp(server):
    server.quit()


def send_html_email_via_smtp(subject, message, recipientList, fromEmail, smtpServer, ccList=[], attachmentPaths=[], message_html=None):
    toEmailString = "; ".join(recipientList)
    ccEmailString = "; ".join(ccList)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromEmail
    msg['To'] = toEmailString
    msg['CC'] = ccEmailString

    # Create the body of the message (a plain-text and an HTML version).
    text = message
    if message_html:
        html = message_html
    else:
        html = """\
        <html>
          <head>
            <title></title>
            <style></style>
          </head>
          <body>
            <font size="4" face="Calibri, Arial, monospace">
            <p>
            %s<br><br>
            </p>
            </font>
          </body>
        </html>
        """ % (message)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    for f in attachmentPaths:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        msg.attach(part)

    try:
        # sendmail function takes 3 arguments: sender's address, recipient's address
        smtpServer.sendmail( fromEmail, recipientList + ccList, msg.as_string() ) #expects a list; not a string!
        print 'SUCCESS: sent email "%s" to "%s"' % (subject, toEmailString)
    except Exception as e:
        print 'ERROR: could not send email "%s" to "%s"' % (subject, toEmailString)
        print e


def send_an_email(subject, body, to_email_list=["example_to_user@gmail.com"]):
    FROM = "example_from_user@gmail.com"
    TO = to_email_list

    SUBJECT = subject
    TEXT = body

    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    SERVER = "smtp.gmail.com"
    myGmail = "example_from_user@gmail.com"
    myGMPasswd = "password_goes_here"

    server = smtplib.SMTP(SERVER, 587)
    server.ehlo()
    server.starttls()
    server.login(myGmail, myGMPasswd)
    server.sendmail(FROM, TO, message)
    server.quit()

    print 'SUCCESS: sent email "%s" to "%s"' % (subject, TO)
