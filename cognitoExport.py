import boto3
import json
import datetime
import time
import sys
import argparse
from colorama import Fore

REGION = ''
USER_POOL_ID = ''
LIMIT = 60
MAX_NUMBER_RECORDS = 10000000
REQUIRED_ATTRIBUTE = None
PROFILE = ''
GROUP = ''

""" Parse All Provided Arguments """
parser = argparse.ArgumentParser(description='Cognito User Pool export', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--user-pool-id', type=str, help="The current pool ID", required=True)
parser.add_argument('--region-current-pool', type=str, default="us-east-1", help="The current pool region", required=False)
parser.add_argument('--user-new-pool-id', type=str, help="The new pool ID", required=True)
parser.add_argument('--region-new-pool', type=str, default="us-east-1", help="The new pool region", required=False)
parser.add_argument('-groups', '--export-groups', nargs='+', type=str, help="List of groups", required=True)
parser.add_argument('--num-records', type=int, help="Max Number of Cognito Records to be exported")
parser.add_argument('--profile', type=str, default='', help="The aws profile")
args = parser.parse_args()

if args.user_pool_id:
    USER_POOL_ID = args.user_pool_id
if args.user_new_pool_id:
    USER_NEW_POOL_ID = args.user_new_pool_id
if args.region_current_pool:
    CURRENT_REGION = args.region_current_pool
if args.region_new_pool:
    NEW_REGION = args.region_new_pool
if args.num_records:
    MAX_NUMBER_RECORDS = args.num_records   
if args.profile:
    PROFILE = args.profile            
if args.export_groups:
    GROUPS = list(args.export_groups) 

if PROFILE:
    session = boto3.Session(profile_name=PROFILE)
    client_current = session.client('cognito-idp', CURRENT_REGION)
    client_new = session.client('cognito-idp', CURRENT_REGION)
else:
    client_current = boto3.client('cognito-idp', CURRENT_REGION)
    client_new = boto3.client('cognito-idp', CURRENT_REGION)


def datetimeconverter(o):
    if isinstance(o, datetime.datetime):
        return str(o)


i = 0;
while i < len(GROUPS):

    def getUser(user):
        usernames = list ()
        user_record = {'username': user['Username'], 'email': None, 'phone_number': None}
        for attr in user['Attributes']:
            if attr['Name'] == 'email':
                user_record['email'] = attr['Value']
            if attr['Name'] == 'phone_number':
                user_record['phone_number'] = attr['Value']
            usernames.append (user_record)
        
        if user_record['email'] is not None:
            return user_record['email']
        
        if user_record['phone_number'] is not None:
            return user_record['phone_number']
            
    def importUsers(cognito_idp_cliend, next_pagination_token ='', Limit = LIMIT):  
        return client_current.list_users_in_group(
            UserPoolId = USER_POOL_ID,
            GroupName = GROUPS[i],
            Limit = Limit,
            NextToken = next_pagination_token,
        ) if next_pagination_token else client_current.list_users_in_group(
            UserPoolId = USER_POOL_ID,
            GroupName = GROUPS[i],
            Limit = Limit
        ) 

    def attributes_check(attributes : list):
        return attributes["Name"] != "sub"

    def createUser(cognito_idp_cliend, user):
        print(Fore.GREEN + "Creating user: " + user['Username'])
        attributes = filter(attributes_check, list(user["Attributes"]))
        
       

        try: 
            if "MFAOptions" in user:
                return client_new.admin_create_user(
                    UserPoolId=USER_NEW_POOL_ID,
                    Username=getUser(user),
                    UserAttributes=list(attributes),
                    MFAOptions=list(MFAOptions),
                    TemporaryPassword='Chang3me*',
                    ForceAliasCreation=True,
                    MessageAction='SUPPRESS',
                )
            else:
                return client_new.admin_create_user(
                    UserPoolId=USER_NEW_POOL_ID,
                    Username=getUser(user),
                    UserAttributes=list(attributes),
                    TemporaryPassword='Chang3me*',
                    ForceAliasCreation=True,
                    MessageAction='SUPPRESS',
                )
            
        except client_new.exceptions.ClientError as err:
            error_message = err.response["Error"]["Message"]
            print(Fore.RED + "Error occured")
            print("Error Reason: " + error_message)

    def addUserToGroup(cognito_idp_cliend, user, group_name):
        print(Fore.GREEN + "Assing user: " + user['Username'] + " to group: " + group_name)
        try:
            return client_new.admin_add_user_to_group(
                UserPoolId= USER_NEW_POOL_ID,
                Username=getUser(user),
                GroupName=group_name
            )
        except client_new.exceptions.ClientError as err:
            error_message = err.response["Error"]["Message"]
            print(Fore.RED + "Error occured")
            print("Error Reason: " + error_message)

 
    pagination_counter = 0
    exported_records_counter = 0
    pagination_token = ""
   
    while pagination_token is not None:
        try:
            user_records = importUsers(
                cognito_idp_cliend = client_current,
                next_pagination_token = pagination_token,
                Limit = LIMIT if LIMIT < MAX_NUMBER_RECORDS else MAX_NUMBER_RECORDS
            )
        except client_current.exceptions.ClientError as err:
            #status = err.response["ResponseMetadata"]["HTTPStatusCode"]
            error_message = err.response["Error"]["Message"]
            print(Fore.RED + "Please Check your Cognito User Pool configs")
            print("Error Reason: " + error_message)
            exit()
        except:
            print(Fore.RED + "Something else went wrong:")
            print(Fore.RED + err.response["Error"]["Message"])
            exit()     

        """ Check if there next paginatioon is exist """
        if set(["PaginationToken","NextToken"]).intersection(set(user_records)):
            pagination_token = user_records['PaginationToken'] if "PaginationToken" in user_records else user_records['NextToken']
        else:
            pagination_token = None

        for user in user_records['Users']:
            createUser(
                cognito_idp_cliend =  client_new,
                user = user
            )

            addUserToGroup(
                cognito_idp_cliend = client_new, 
                user = user, 
                group_name = GROUPS[i]
            )

            exported_records_counter +=  1
           
        """ Display Proccess Infor """
        pagination_counter += 1
        print(Fore.YELLOW + 'Total '+ GROUPS[i] +' Exported Records: ' + str(exported_records_counter))

        if MAX_NUMBER_RECORDS and exported_records_counter >= MAX_NUMBER_RECORDS:
            print(Fore.GREEN + "INFO: Max Number of Exported  "+GROUPS[i]+" Reached")
            break    

        """ Cool Down before next batch of Cognito Users """
        time.sleep(0.15)
   
    i = i + 1;   

