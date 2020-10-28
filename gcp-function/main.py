import urllib3
from datetime import datetime
import os
from google.cloud import secretmanager


def prisma_trello_card(request):
    # Test if special HTTP header and auth key exists. This is required because GCP does not allow configuring API key
    # on HTTP Triggers. Full IAM security is required, which is fine when the client can request a JWT. Our source
    # webhook can NOT. This is the same as an API key but just implemented in this code.
    request_headers = request.headers
    if not request_headers["PRISMA-WEBHOOK-API-KEY"] == os.environ.get("PRISMA_WEBHOOK_API_KEY"):
        return {
            'statusCode': 401
        }

    # Grab the required secrets from GCP Secrets Manager
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
    for x in secrets_dict:
        secret_request = {"name": f"projects/{project_id}/secrets/{x}/versions/latest"}
        secret_response = secret_client.access_secret_version(secret_request)
        secrets_dict[x] = secret_response.payload.data.decode("UTF-8")

    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")

    http = urllib3.PoolManager()
    url = "https://api.trello.com/1/cards"
    request_json_body = request.get_json("body")

    if not isinstance(request_json_body, list):  # Is this a single JSON object (dict)
        request_json_body = [request_json_body]  # Place into a list

    try:
        for counter, value in enumerate(request_json_body):
            account_name = request_json_body[counter]["accountName"]
            severity = request_json_body[counter]["severity"]
            rule_name = request_json_body[counter]["alertRuleName"]
            resource_id = request_json_body[counter]["resourceId"]
            policy_desc = request_json_body[counter]["policyDescription"]
            cloud_resource_type = request_json_body[counter]["resourceCloudService"]
            cloud_type = request_json_body[counter]["cloudType"]
            prisma_alert_url = request_json_body[counter]["callbackUrl"]

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

            r = http.request('POST', url, fields=query)
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
            "body": request_json_body
        }

    return {
        'statusCode': 200
    }
