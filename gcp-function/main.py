import urllib3
import requests
from datetime import datetime
import os
from google.cloud import secretmanager
import json


def prisma_trello_card(request):
    # Start by grabbing the required secrets from GCP Secrets Manager
    secret_client = secretmanager.SecretManagerServiceClient()
    secrets_dict = {
        # Use ENV variables to grab the name of the GCP secret and initialise a dict
        os.environ.get("TRELLO_KEY_SECRET"): "tbc",
        os.environ.get("TRELLO_TOKEN_SECRET"): "tbc",
        os.environ.get("TRELLO_IDLIST_SECRET"): "tbc"
    }

    # Get the current Project ID using reserved env variable. This should be changed if secrets exist in diff project
    # GCP_PROJECT appears to only work with some code versions (e.g. Python 3.7 and NOT 3.8!
    # project_id = os.environ.get("GCP_PROJECT")
    project_id = os.environ.get("MY_SECRETS_PROJECT")

    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")

    for x in secrets_dict:
        secret_request = {"name": f"projects/{project_id}/secrets/{x}/versions/latest"}
        secret_response = secret_client.access_secret_version(secret_request)
        secrets_dict[x] = secret_response.payload.data.decode("UTF-8")

    url = "https://api.trello.com/1/cards"
    request_json = request.get_json("body")
    debug_array = []

    if isinstance(request_json, list):   # If received body is an array of JSON objects
        try:
            debug_array.append("THIS IS A LIST!")
            for index, value in enumerate(request_json):
                # http = urllib3.PoolManager()
                debug_array.append("WE ARE IN A FOR LOOP! HERE IS THE index...... ")
                debug_array.append(index)
                account_name = request_json[index]["accountName"]
                severity = request_json[index]["severity"]
                rule_name = request_json[index]["alertRuleName"]
                resource_id = request_json[index]["resourceId"]
                policy_desc = request_json[index]["policyDescription"]
                cloud_resource_type = request_json[index]["resourceCloudService"]
                cloud_type = request_json[index]["cloudType"]
                prisma_alert_url = request_json[index]["callbackUrl"]

                # Gather key pieces of info from Prisma Alert JSON
                # name given to the card (title)
                name = 'Prisma Alert: ' + "| " + date_time + " | " + resource_id + " " + rule_name

                # String for the card body
                desc = 'Alert details \n' + "Link to alert: " + prisma_alert_url + "\n" \
                       + "Account name: " + account_name + "\n" \
                       + "Cloud platform: " + cloud_type + "\n" + "Resource type: " + cloud_resource_type + "\n" \
                       + "Policy description: " + policy_desc + "\n"

                query = {
                    'key': secrets_dict[os.environ.get("TRELLO_KEY_SECRET")],
                    'token': secrets_dict[os.environ.get("TRELLO_TOKEN_SECRET")],
                    'idList': secrets_dict[os.environ.get("TRELLO_IDLIST_SECRET")],
                    'pos': 'top',
                    'name': name,
                    'desc': desc
                }

                # r = http.request('POST', url, fields=query)
                r = requests.post(url, params=query)
                r.close()

                # print(r.data)

        except:
            # Reflect the request back as a response. This will greatly aid troubleshooting...
            # so one can analyse the JSON structure against what is expected.
            # This needs to be a 200 response so it will pass the Prisma integration test
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": request_json
            }
    else:   # If received body is a single JSON object
        try:
            http = urllib3.PoolManager()
            debug_array.append("THIS IS **NOT** A LIST")
            account_name = request_json["accountName"]
            severity = request_json["severity"]
            rule_name = request_json["alertRuleName"]
            resource_id = request_json["resourceId"]
            policy_desc = request_json["policyDescription"]
            cloud_resource_type = request_json["resourceCloudService"]
            cloud_type = request_json["cloudType"]
            prisma_alert_url = request_json["callbackUrl"]

            # Gather key pieces of info from Prisma Alert JSON
            # name given to the card (title)
            name = 'Prisma Alert: ' + "| " + date_time + " | " + resource_id + " " + rule_name

            # String for the card body
            desc = 'Alert details \n' + "Link to alert: " + prisma_alert_url + "\n" \
                   + "Account name: " + account_name + "\n" \
                   + "Cloud platform: " + cloud_type + "\n" + "Resource type: " + cloud_resource_type + "\n" \
                   + "Policy description: " + policy_desc + "\n"

            query = {
                'key': secrets_dict[os.environ.get("TRELLO_KEY_SECRET")],
                'token': secrets_dict[os.environ.get("TRELLO_TOKEN_SECRET")],
                'idList': secrets_dict[os.environ.get("TRELLO_IDLIST_SECRET")],
                'pos': 'top',
                'name': name,
                'desc': desc
            }

            # r = http.request('POST', url, fields=query)
            r = requests.post(url, params=query)

            print(r.data)
        except:
            # Reflect the request back as a response. This will greatly aid troubleshooting...
            # so one can analyse the JSON structure against what is expected.
            # This needs to be a 200 response so it will pass the Prisma integration test
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": request_json
            }

    return r.json()
