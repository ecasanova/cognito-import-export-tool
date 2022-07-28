import boto3
import json
import datetime
import time
import sys
import argparse
from colorama import Fore

REGION = ''
USER_POOL_ID = ''
USER_NEW_POOL_ID = ''
LIMIT = 60
MAX_NUMBER_RECORDS = 10000
PROFILE = ''
GROUPS = []

def password_check(passwd):
    SpecialSym =['$', '@', '#', '%']
    val = True
      
    if len(passwd) < 6:
        print(Fore.RED + 'Password length should be at least 6')
        val = False
          
    if len(passwd) > 20:
        print(Fore.RED + 'Password length should be not be greater than 8')
        val = False
          
    if not any(char.isdigit() for char in passwd):
        print(Fore.RED + 'Password should have at least one numeral')
        val = False
          
    if not any(char.isupper() for char in passwd):
        print(Fore.RED + 'Password should have at least one uppercase letter')
        val = False
          
    if not any(char.islower() for char in passwd):
        print(Fore.RED + 'Password should have at least one lowercase letter')
        val = False
          
    if not any(char in SpecialSym for char in passwd):
        print(Fore.RED + 'Password should have at least one of the symbols $@#')
        val = False
    if val:
        return val

""" Parse All Provided Arguments """
parser = argparse.ArgumentParser(description='Cognito User Pool export / import', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--user-pool-id', type=str, help="The current pool ID for perform the export", required=True)
parser.add_argument('--region-current-pool', type=str, default="us-east-1", help="The current pool region for perform the export", required=False)
parser.add_argument('--user-new-pool-id', type=str, help="The new pool ID for perform the import", required=True)
parser.add_argument('--region-new-pool', type=str, default="us-east-1", help="The new pool region for perform the import", required=False)
parser.add_argument('--groups', nargs='+', type=str, help="List of user groups (names separated by spaces)", required=True)
parser.add_argument('--profile-current-pool', type=str, default='default', help="The aws profile for perform the export", required=False)
parser.add_argument('--profile-new-pool', type=str, default='default', help="The aws profile for perform the import", required=False)
parser.add_argument('--new-password', default='Ch@ng3me*', type=str, help="The new password for the users in the new pool", required=False)
parser.add_argument('--num-records', type=int, help="Max Number of Cognito Records to be exported")

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

if args.profile_current_pool:
    PROFILE_CURRENT = args.profile_current_pool    

if args.profile_new_pool:
    PROFILE_NEW = args.profile_new_pool   

if args.groups:
    GROUPS = list(args.groups) 

if args.new_password:
   NEW_PASSWORD = args.new_password

if NEW_PASSWORD:
    if password_check(NEW_PASSWORD):
        print(Fore.GREEN + 'Password is valid')
    else:
        print(Fore.RED + 'Password is invalid')
        sys.exit(1)

session_current = boto3.Session(profile_name=PROFILE_CURRENT)
client_current = session_current.client('cognito-idp', CURRENT_REGION)

session_new = boto3.Session(profile_name=PROFILE_NEW)
client_new = session_new .client('cognito-idp', NEW_REGION)

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
                    TemporaryPassword=NEW_PASSWORD,
                    ForceAliasCreation=True,
                    MessageAction='SUPPRESS',
                )
            else:
                return client_new.admin_create_user(
                    UserPoolId=USER_NEW_POOL_ID,
                    Username=getUser(user),
                    UserAttributes=list(attributes),
                    TemporaryPassword=NEW_PASSWORD,
                    ForceAliasCreation=True,
                    MessageAction='SUPPRESS',
                )
            
        except client_new.exceptions.ClientError as err:
            error_message = err.response["Error"]["Message"]
            print(Fore.RED + "Error occured")
            print("Error Reason: " + error_message)

    def addUserToGroup(cognito_idp_cliend, user, group_name):
        print(Fore.GREEN + "Added " + user['Username'] + " to group: " + group_name)
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