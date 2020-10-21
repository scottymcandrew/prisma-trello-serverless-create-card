# prisma-trello-lambda-create-card

These Python scripts are to allow the sending of Prisma Cloud alerts (in JSON format) to Trello to create a card.

This function is required since Trello can not ingest JSON.

In this current version of the repo, there is a function for Lambda and GCP Functions.

# Setup instructions

1. Create a new Lambda function on AWS using Python 3.x. Use the code in this repo.
2. Add the trello "key", "token" and "idList" environment variables. The latter identifies the list where the card will be created.
3. Add an API Gateway Trigger. If selecting an HTTP API, then an API key can not be configured (it will be open). If you create a REST API you can specify a key, of which will be referenced as an HTTP header of "x-api-key".
4. **Optional** Test API with a tool such as Postman. In this repo is a sample Prisma Alert JSON.
5. On Prisma Cloud: set up a new Webhook integration. Set webhook URL to the Lambda API gateway URL. Set the x-api-key HTTP header if using a key (preferred!). Test this webhook using the test button. If this works, proceed to the next step.
6. On Prisma Cloud: create a new alert rule, target the accounts required, select policy/policies and for alert notification select the webhook integration we just created. As a test I would suggest targeting a simple policy, such as "AWS S3 buckets are accessible to public". Then create a storage bucket with public access.
7. Wait for the resource to be alerted and verify card creation on Trello.
