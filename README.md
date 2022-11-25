## Installation

In order to use this script you should have Python 2 or Python 3 installed on your platform

- run `pip install -r requirements.txt` (Python 2) or `pip3 install -r requirements.txt` (Python 3)
- Install AWS Cli [https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html]
- Setup AWS credentials [https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html]

## AWS CLI Credentials example

Edit this file: ~/.aws/credentials and add the different profile credentials

```
[default]
aws_access_key_id = XXXXX
aws_secret_access_key = XXXXXXX

[profile]
aws_access_key_id = XXXXXXX
aws_secret_access_key = XXXXXXXX
```

## Run export / import

To start export / import proccess you shout run next command (**Note**: use `python3` if you have Python 3 instaled)

- `$ python3 CognitoExport.py --user-pool-id 'us-east-2_XXXXXXX' --user-new-pool-id 'us-east-2_XXXXXXXX' --region-current-pool us-east-2 --region-new-pool us-east-2 --profile-current-pool xxxx --profile-new-pool xxxx --new-password xxxxxxx --groups Admins Users`

### Script Arguments

- `--user-pool-id` [__Required__] - The user pool ID for the user pool on which the export should be performed
- `--user-new-pool-id` [__Required__] - The user pool ID for the user pool on which the import should be performed
- `--groups` [__Required__] - The group list on which the export/import should be performed (names separated by spaces)
- `--profile-current-pool` [_Optional_] - A named profile is a collection of settings and credentials that you can apply to a AWS CLI command _Default_: `default`
- `--profile-new-pool` [_Optional_] - A named profile is a collection of settings and credentials that you can apply to a AWS CLI command _Default_: `default`
- `--region-current-pool` [_Optional_] - The user pool region the user pool on which the export should be performed _Default_: `us-east-1`
- `--region-new-pool` [_Optional_] - The user pool region the user pool on which the import should be performed _Default_: `us-east-1`
- `--new-password` [_Optional_] - The new password for the users in the new pool _Default_: `Ch@ng3me*`
- `--num-records` [_Optional_] - Max Number of Cognito Records to be exported _Default_: `10000`
