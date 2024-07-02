import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import json
from io import StringIO
import csv
client = boto3.client('dynamodb')
def PythonToDB(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }
    
def DBToPython(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }
    
def SendCsv(data):
        # Convert the dictionary to CSV format
    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=['id','First Name','Last Name','veg','Gender','Attendance','designation','Team ID','Name of the institute','Mobile number','email','Date & Time'])
    csv_writer.writeheader()
    for row in data:
        csv_writer.writerow(DBToPython(row))

    # Create an API Gateway response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="data.csv"'
        },
        'body': csv_data.getvalue()
    }

def lambda_handler(event, context):
    if 'body' in event:# data upload from pytho code happens hear
        print(event['body'])
        data = json.loads(event['body'])
        print(data)
 #       print(type(data['Veg']))
        ssi_total=0
        sssjkl_total=0
        tot=1
        if data['Team ID']=='SSSJKL-PMUSP Yojna Students':
            sssjkl_total=1
        else:
            ssi_total = 1
            
       # try:
        datatype={"Data_Type" : "college", "name": data['Name of the institute']}
        response = client.put_item(TableName='dataList', Item=PythonToDB(datatype))
        datatype={"Data_Type" : "mentor", "name": data['Team ID']}
        response = client.put_item(TableName='dataList', Item=PythonToDB(datatype))
        response = client.put_item(TableName='AICET', Item=PythonToDB(data))
        response = client.update_item(
    TableName='AICTE_count',
    Key={'Category': {'S': 'All'}},
    UpdateExpression='SET tot = tot + :val1, ssi_total = ssi_total + :val2, sssjkl_total = sssjkl_total + :val3',
    ExpressionAttributeValues={
        ':val1': {'N': str(tot)},
        ':val2': {'N': str(ssi_total)},
        ':val3': {'N': str(sssjkl_total)}
    }
)
        return "sucesses"
       # except:
       #     return "error in upload"
    else:
        query = event['queryStringParameters']
        print(event)
        typ= query['type']
        
        if typ == 'id' :#sends details of the persion with the ID number
            ID = query['id']
            print(ID)
            response = client.get_item( TableName='AICET', Key={"id": {"S": ID}})
            if 'Item' in response:
                respon=DBToPython(response['Item'])
                print(respon)
                #response = client.get_item( TableName='AICET', Key={"id": {"S": respon['Mentor_ID']}},ProjectionExpression='#N',ExpressionAttributeNames={'#N': 'Name'})
                scan_params = {
                'TableName': 'AICET',
                'ProjectionExpression': '#first_name, #last_name',
                'FilterExpression': '#team_id = :id and designation = :Designation',
                'ExpressionAttributeValues': {
                    ':id': {'S': respon['Team ID']},
                    ':Designation': {'S': 'Mentor'}
                },
                'ExpressionAttributeNames': {
                    '#team_id': 'Team ID',
                    '#first_name': 'First Name',
                    '#last_name': 'Last Name'
                }
            }



                response = client.scan(**scan_params)#code to obtain mentor name
                mentornames=''
                coma=False
                for item in response['Items']:
                    if coma:
                        mentornames=mentornames +', '
                    item=DBToPython(item)
                    mentornames+=item['First Name']+' '+item['Last Name']
                    coma=True
                    
                print(mentornames)
                respon.update({'Mentorname(s)': mentornames})
                print(respon)
                return respon
            else:
                return "ID not found"
        elif typ == 'atte':#updates attendance status to true and correct any mistake in meal preference
            ID = query['id']
            print(ID)
            response = client.get_item( TableName='AICET', Key={"id": {"S": ID}})
            
            if 'Item' in response:
                data=DBToPython(response['Item'])
                sssjkl_present=0
                ssi_present=0
                men=0
                women=0
                if data['Team ID']=='SSSJKL-PMUSP Yojna Students':
                    sssjkl_present=1
                else:
                    ssi_present = 1
                if data['Gender']=='Male':
                    men=1
                else:
                    women=1
                response = client.update_item(
                                                TableName='AICET',
                                                Key={'id': {'S': ID}},
                                                UpdateExpression='SET Attendance = :val1, #DateTime = :val2, veg = :val3',
                                                ExpressionAttributeValues={
                                                    ':val1': {'BOOL': True},
                                                    ':val2': {'S': query['update']},
                                                    ':val3': {'S': query['veg']}
                                                },
                                                ExpressionAttributeNames={
                                                    '#DateTime': 'Date & Time'
                                                }
                                            )
                response = client.update_item(
                TableName='AICTE_count',
                Key={'Category': {'S': 'All'}},
                UpdateExpression='SET present = present + :val1, men = men + :val2, ssi_present = ssi_present + :val3, women = women + :val4, sssjkl_present = sssjkl_present + :val5',
                ExpressionAttributeValues={
                    ':val1': {'N': '1'},
                    ':val2': {'N': str(men)},
                    ':val3': {'N': str(ssi_present)},
                    ':val4': {'N': str(women)},
                    ':val5': {'N': str(sssjkl_present)},
                }
            )
                return "done"
            else:
                return "data not found"
        elif typ == 'total':# returns data to the front screen of the web application/////////////////////
            response = client.get_item( TableName='AICTE_count', Key={'Category': {'S': 'All'}})
            data=DBToPython(response['Item'])
            print(data)
            
            front={'totalUsers':data['tot'],'shiveData':data['sssjkl_present'],'totalmen':data['men'],'totalwomen':data['women'],'shivadatatotal':data['sssjkl_total'],'ddrData':data['ssi_present'],'ddrdata':data['ssi_total'],'registeredUsers':data['present'],'newRegistratio_total':data['newRegistratio_total']}

            return front
        elif typ=='list':
            need=query['need']
            if need=='institution':
                typp='college'
                response = client.query(
                TableName='dataList',
                KeyConditionExpression='Data_Type = :partition_key_value',
                ExpressionAttributeValues={
                    ':partition_key_value': {'S': 'college'}
                },ProjectionExpression='#n',  # Using an alias for the 'name' attribute
                ExpressionAttributeNames={
                    '#n': 'name'  # Alias for the 'name' attribute
                }
                )
                names = [item['name']['S'] for item in response['Items']]
                print(names)
                return names
            elif need=='mentor':
                response = client.query(
                TableName='dataList',
                KeyConditionExpression='Data_Type = :partition_key_value',
                ExpressionAttributeValues={
                    ':partition_key_value': {'S': 'mentor'}
                },ProjectionExpression='#n',  # Using an alias for the 'name' attribute
                ExpressionAttributeNames={
                    '#n': 'name'  # Alias for the 'name' attribute
                }
                )
                names = [item['name']['S'] for item in response['Items']]
                print(names)
                return names
            elif need=='complete':
                response = client.query(
                TableName='dataList',
                KeyConditionExpression='Data_Type = :partition_key_value',
                ExpressionAttributeValues={
                    ':partition_key_value': {'S': 'mentor'}
                },ProjectionExpression='#n',  # Using an alias for the 'name' attribute
                ExpressionAttributeNames={
                    '#n': 'name'  # Alias for the 'name' attribute
                }
                )
                mentor = [item['name']['S'] for item in response['Items']]
                response = client.query(
                TableName='dataList',
                KeyConditionExpression='Data_Type = :partition_key_value',
                ExpressionAttributeValues={
                    ':partition_key_value': {'S': 'college'}
                },ProjectionExpression='#n',  # Using an alias for the 'name' attribute
                ExpressionAttributeNames={
                    '#n': 'name'  # Alias for the 'name' attribute
                }
                )
                colle = [item['name']['S'] for item in response['Items']]
                data ={"college":colle,"mentor":mentor}
                print(data)
                return data
        
        elif typ == 'newreg':
            data= json.loads(query['data'])
            response = client.get_item( TableName='AICTE_count', Key={'Category': {'S': 'All'}},ProjectionExpression='tot')
            data['id']=str(1 + int(response['Item']['tot']['N'])).zfill(4)
            print(data)
            print(response)
            tot=1
            newRegistratio_total=1
            present = 1
            men=0
            women=0
            if data['Gender']=='Male':
                men=1
            else:
                women=1
            datatype={"Data_Type" : "college", "name": data['Name of the institute']}
            response = client.put_item(TableName='dataList', Item=PythonToDB(datatype))
            datatype={"Data_Type" : "mentor", "name": data['Team ID']}
            response = client.put_item(TableName='dataList', Item=PythonToDB(datatype))
            response = client.put_item(TableName='AICET', Item=PythonToDB(data))
            response = client.update_item(
                                            TableName='AICTE_count',
                                            Key={'Category': {'S': 'All'}},
                                            UpdateExpression='SET tot = tot + :val1, newRegistratio_total = newRegistratio_total + :val2, present = present + :val3, men = men + :val4, women = women + :val5',
                                            ExpressionAttributeValues={
                                                ':val1': {'N': str(tot)},
                                                ':val2': {'N': str(newRegistratio_total)},
                                                ':val3': {'N': str(present)},
                                                ':val4': {'N': str(men)},
                                                ':val5': {'N': str(women)}
                                            }
                                         )
            return 'sucesses'
        elif typ == 'Query':
            need=query['need']
            #scan_params={}
            if (need == 'total'):
                scan_params = {
                                    'TableName': 'AICET',
                                    'FilterExpression': 'Attendance = :val1 OR Attendance = :val2',
                                    'ExpressionAttributeValues': {
                                    ':val1': {'BOOL': True},
                                    ':val2': {'S':'true'}
                                    }
                                  }
            elif (need == 'ddrData'):
                scan_params = {
                                    'TableName': 'AICET',
                                    'FilterExpression': '(Attendance = :val1 OR Attendance = :val2) and #team_id <> :val3',
                                    'ExpressionAttributeValues': {
                                    ':val1': {'BOOL': True},
                                    ':val2': {'S':'true'},
                                    ':val3': {'S': 'SSSJKL-PMUSP Yojna Students'}
                                    },
                                    'ExpressionAttributeNames': {
                                    '#team_id': 'Team ID'}
                                  }
            elif (need == 'shiveData'):
                scan_params = {
                                    'TableName': 'AICET',
                                    'FilterExpression': '(Attendance = :val1 OR Attendance = :val4) and #team_id = :val2 and #mobno <> :val3',
                                    'ExpressionAttributeValues': {
                                    ':val1': {'BOOL': True},
                                    ':val2': {'S': 'SSSJKL-PMUSP Yojna Students'},
                                    ':val3': {'S':'Nil'},
                                    ':val4': {'S':'true'}
                                    },
                                    'ExpressionAttributeNames': {
                                    '#team_id': 'Team ID',
                                    '#mobno': 'Mobile number'
                                    }
                                  }
            elif (need == 'college'):
                name=query['name']
                stat=query['status']
                if stat == 'true':
                    scan_params = {
                                    'TableName': 'AICET',
                                    'FilterExpression': '#college = :val2 and #mobno <> :val3',
                                    'ExpressionAttributeValues': {
                                    ':val2': {'S': name},
                                    ':val3': {'S':'Nil'}
                                    },
                                    'ExpressionAttributeNames': {
                                    '#college': 'Name of the institute',
                                    '#mobno': 'Mobile number'
                                    }
                                  }
                else:
                    scan_params = {
                                    'TableName': 'AICET',
                                    'FilterExpression': '(Attendance = :val1 OR Attendance = :val4) and #college = :val2 and #mobno <> :val3',
                                    'ExpressionAttributeValues': {
                                    ':val1': {'BOOL': True},
                                    ':val2': {'S': name },
                                    ':val3': {'S':'Nil'},
                                    ':val4': {'S':'true'}
                                    },
                                    'ExpressionAttributeNames': {
                                    '#college': 'Name of the institute',
                                    '#mobno': 'Mobile number'
                                    }
                                  }
            elif (need == 'mentor'):
                fname=query['fname']
                lname=query['lname']
                team_id=fname
                print(team_id)
                scan_params = {
                                        'TableName': 'AICET',
                                        'FilterExpression': '#team_id = :val1 and #mobno <> :val2',
                                        'ExpressionAttributeValues': {
                                        ':val1': {'S': team_id },
                                        ':val2': {'S':'Nil'}
                                        },
                                        'ExpressionAttributeNames': {
                                        '#team_id': 'Team ID',
                                        '#mobno': 'Mobile number'
                                        }
                                      }
            response = client.scan(**scan_params)
            print(response)
            print(response['Items'])
            return SendCsv(response['Items'])
        else:
            return "spellig nokki ayakedaa"