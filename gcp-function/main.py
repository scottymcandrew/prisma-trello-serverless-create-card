import urllib3
from datetime import datetime
import os


def prisma_trello_card(request):
    http = urllib3.PoolManager()
    url = "https://api.trello.com/1/cards"
    request_json = request.get_json("body")

    # Gather key pieces of info from Prisma Alert JSON
    try:
        account_name = request_json["accountName"]
        severity = request_json["severity"]
        rule_name = request_json["alertRuleName"]
        resource_id = request_json["resourceId"]
        policy_desc = request_json["policyDescription"]
        cloud_resource_type = request_json["resourceCloudService"]
        cloud_type = request_json["cloudType"]
        prisma_alert_url = request_json["callbackUrl"]
        now = datetime.now()
        date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
    except:
        # Where the JSON sent in the request does not match the expected format (e.g. an API test),
        # just respond with 200 to prove function runs.
        return {
            'statusCode': 200
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
        'name': name,
        'desc': desc
    }

    r = http.request(
        'POST',
        url,
        fields=query)

    print(r.data)

    return {
        'statusCode': 200
    }
