import qrcode
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import csv
import requests
from boto3.dynamodb.types import TypeSerializer


eannu=1
url = 'https://6udmxpz3sdcrnt6zcdhbiuiuhiqezb.lambda-url.ap-south-1.on.aws/'# replace with lambda api
filename = r"C:\D drive\college project\data.csv"  #datat file
fieldnames = ["id", "Name", "School","Mentor_ID",]


class MyCustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def PythonToDB(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def QRcodeGenerator(data,name):
    # Convert dictionary to string
    data_str = str(data)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(data_str)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Load the bold font
    font_path = "arialbd.ttf"  # Path to the bold font file
    font_size = 33  # Font size
    font = ImageFont.truetype(font_path, font_size)

    qr_width = 530
    qr_height = 530

    # Resize the QR code image to the specified width and height
    qr_image = qr_image.resize((qr_width, qr_height))

    # Load the background image
    background_image_path = r'C:\D drive\college project\QRbaground.jpg'
    background_image = Image.open(background_image_path)

    # Load a font
    name_font_size = 60
    id_font_size = 45
    name_font = ImageFont.truetype(r"C:\D drive\college project\Grandstander-SemiBold.ttf", name_font_size)
    id_font = ImageFont.truetype(r"C:\D drive\college project\Grandstander-SemiBold.ttf", id_font_size)

    # Paste the QR code image onto the background image at the new position
    background_image.paste(qr_image, (285 , 1134 ))

    # Create a drawing object
    draw = ImageDraw.Draw(background_image)

    # Specify the texts and the positions to print
    id = "ID : "+data
    x1, y1 = 172, 400  # Specify the coordinates for text1
    x2, y2 = ((background_image.width - 130)//2), 1625   # Specify the coordinates for text2

    # Print the texts on the image
    draw.text((x1, y1), name, fill="black", font=name_font)
    draw.text((x2, y2), id, fill="black", font=id_font)

    # Save or display the image
    background_image.save(r"C:\D drive\college project\codes\SentQr.png")
    #background_image.show()


    # Save the image
    return r"C:\D drive\college project\codes\SentQr.png"
    #qr_image.save(qr_image_path)

def SentEmail(toemail,qr_image_path):
    email_address = "place your email id"
    password = "place you email app password"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = email_address
    message["To"] = toemail
    message["Subject"] = "QR Code to register IDE BOOTCAMP @ SNGCE"

    # Add body to email
    message.attach(MIMEText("!!Greetings from SNGCE. All SNGCE Mentors are requested to register at the registration counter. your name using the QR code send to your mailid", "plain"))

    # Open the file in binary mode
    with open(qr_image_path, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEImage(attachment.read(), _subtype="png")
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(qr_image_path)}",
        )
        message.attach(part)

    pdf_path=r"C:\D drive\college project\guidelines.pdf"
    with open(pdf_path, "rb") as pdf_attachment:
            part = MIMEApplication(pdf_attachment.read(), _subtype="pdf")
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(pdf_path)}",
            )
            message.attach(part)    


        # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, password)
        rejected_recipients = server.sendmail(email_address, toemail, message.as_string())
    if not rejected_recipients:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email to the following recipients: {rejected_recipients}")

def read_csv_to_dict(filename):
    data = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(dict(row))
    return data


i=228                                 #change id hear for continuation

data = read_csv_to_dict(filename)
for row in data:
    cleaned_dict = {key.strip(): value.strip() for key, value in row.items()}
    row=cleaned_dict
    flag=True
    if row['veg'].strip()== '1':
        row['veg']= 'veg'
    else:
        row['veg']= 'non veg'
    row.update({'id': str(i).zfill(4),'Attendance' : False,'Date & Time':"" })
    #file_exists = os.path.isfile(csv_file_path)
    i += 1
    print(row)
    while True:
        flag=True
        try:
            
            response = requests.post(url, json=(row)) #send datat to aws server
            print('DB insertion ' + response.text)
            if response.text != 'sucesses':
                raise MyCustomError("error in lamda function")
            name=row['First Name']+" "+row['Last Name']
            SentEmail(row['email'],QRcodeGenerator(row['id'],name)) # function work hear
        except:
            print("\n\nnetwork error..!!")
            flag=False
        if not flag:
            print("network error has happend \n datat upload and sending emails has failed at : ",end="")
            print(row)
            tryflag=input("press N to terminate...!! / press any other key and enter to Retry : ")
            if(tryflag in ('N','n' )):
                break   
        else:
            break
    if not flag:
        break
    





