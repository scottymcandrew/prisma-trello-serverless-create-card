import json
import urllib3
from datetime import datetime
import os


def lambda_handler(event, context):
    http = urllib3.PoolManager()
    url = "https://api.trello.com/1/cards"
    data = json.loads(event['body'])

    # Gather key pieces of info from Prisma Alert JSON
    try:
        account_name = data["accountName"]
        severity = data["severity"]
        rule_name = data["alertRuleName"]
        resource_id = data["resourceId"]
        policy_desc = data["policyDescription"]
        cloud_resource_type = data["resourceCloudService"]
        cloud_type = data["cloudType"]
        prisma_alert_url = data["callbackUrl"]
        now = datetime.now()
        date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
    except:
        # Reflect the request back as a response. This will greatly aid troubleshooting...
        # so one can analyse the JSON structure against what is expected.
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": data
        }

    # name given to the card (title)
    name = 'Prisma Alert: ' + "| " + date_time + " | " + resource_id + " " + rule_name

    # String for the card body
    desc = 'Alert details \n' + "Link to alert: " + prisma_alert_url + "\n" \
           + "Account name: " + account_name + "\n" \
           + "Cloud platform: " + cloud_type + "\n" + "Resource type: " + cloud_resource_type + "\n" \
           + "Policy description: " + policy_desc + "\n"

    query = {
        'key': os.environ.get("key"),
        'token': os.environ.get("token"),
        'idList': os.environ.get("idList"),
        'pos': 'top',
        'name': name,
        'desc': desc
    }

    r = http.request(
        'POST',
        url,
        fields=query)

    print(r.data)

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
