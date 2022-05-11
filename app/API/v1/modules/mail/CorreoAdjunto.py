# import necessary packages
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
 
# create message object instance
msg = MIMEMultipart()
 
# setup the parameters of the message
password = "u8m7&KNJ4"
msg['From'] = "envio@fundacioncchc.cl"
msg['To'] = "ecarrizo@fundacioncchc.cl"
msg['Subject'] = "Subscription"

# adjuntando PDF 
pdf = MIMEApplication(open("69ce6b13-b7c0-482c-877d-f042575a2c26.pdf", 'rb').read())
pdf.add_header('Content-Disposition', 'attachment', filename= "69ce6b13-b7c0-482c-877d-f042575a2c26.pdf")
msg.attach(pdf)

# create server
server = smtplib.SMTP('smtp.gmail.com: 587')
server.starttls()
 
# Login Credentials for sending the mail
server.login(msg['From'], password)

# send the message via the server.
server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()
 
print ("successfully sent email to: ", msg['To'])