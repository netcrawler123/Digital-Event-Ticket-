# Digital event ticket
An event registration system where we can automatically send emails to all the participants in a csv file with 
an event ticket as an attachment which contains a unique QR code and the participant’s name, 
this ticket is to be scanned at the event registration desk using our app, this will mark the 
participants attendance, and the event team can check the current status of registration using 
our website. This project is done using AWS Lambda, DynamoDB and Python.
- The [final_code.py](final_code.py) is used to send unique QRcodes to the email ids in [data.csv](data.csv) with [QRbaground.png](QRbaground.png) where the name field will be filled automatically and the data from the csv file will be uploaded to Dynamo DB 
- A mobile app is then used to scan the QR code to verify the ticket and mark their attendance.
- This participation status can be viewed by a web application in real time
- The [lambda_function.py](lambda_function.py) runs in aws lambda and is used by the mobile app to verify and mark the participants attandence and is also used by the web application to retrive the requested participation status and also to download the datat as a csv file
