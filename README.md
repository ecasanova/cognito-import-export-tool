## Instalation

In order to use this script you should have Python 2 or Python 3 installed on your platform

- run `pip install -r requirements.txt` (Python 2) or `pip3 install -r requirements.txt` (Python 3)

## Run export

To start export proccess you shout run next command (**Note**: use `python3` if you have Python 3 instaled)

- `$ python3 CognitoExport.py --user-pool-id 'us-east-2_XXXXXXX' --user-new-pool-id 'us-east-2_XXXXXXXX' --region-current-pool us-east-2 --region-new-pool us-east-2 -groups TestGroup`

### Script Arguments

- `--user-pool-id` [__Required__] - The user pool ID for the user pool on which the export should be performed
- `--user-new-pool-id` [__Required__] - The user pool ID for the user pool on which the import should be performed
- `-groups` [__Required__] - The group list on which the export/import should be performed
- `--region-current-pool` [_Optional_] - The user pool region the user pool on which the export should be performed _Default_: `us-east-1`
- `--region-new-pool` [_Optional_] - The user pool region the user pool on which the import should be performed _Default_: `us-east-1`
