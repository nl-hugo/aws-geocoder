
A REST API that computes the driving distance between two zip codes (Dutch only!). The API is hosted as an AWS Lambda function.

Note that this function relies on the routing capabilities of the [OSRM Project]. Since it is a demo server, too many requests can lead to 429 errors.


## Deployment

Run the following steps to deploy the code to your AWS environment. This requires an AWS account and the AWS CLI.

### Create stack
    
Create the stack using the CloudFormation template:

    aws cloudformation create-stack --stack-name serverless-Geocoder --template-body file://aws-stack.yml --capabilities CAPABILITY_NAMED_IAM


### Package the code

Install dependencies

    pip install -r requirements.txt -t ./package

Add dependencies to zip archive

    7z a geopy.zip ./package

Add lambda function to zip archive

    7z a geopy.zip lambda_function.py


### Deploy function code

Update the function code. If this results in a `ResourceNotFoundException`, this means that CloudFormation is still creating the stack. Check the status in the CloudFormation dashboard and try again in a few moments.

    aws lambda update-function-code --function-name serverless-Geocoder --zip-file fileb://geopy.zip

In the Lambda Management Console, run a test event with the following content to ensure correct functioning of the lambda function:

    {
      "pathParameters": {
        "zip_from": "3512JC",
        "zip_to": "3584AA"
      }
    }

## Invoke the API

In the API Gateway Management console, find the API url on the `Dashboard` tab:

    https://{unique-aws-id}.execute-api.{region}.amazonaws.com/prod/

Use the URL to invoke the api and don't forget to add `geocoder/` and the zip codes as path arguments:

    https://{unique-aws-id}.execute-api.{region}.amazonaws.com/prod/geocoder/3512JC/3584AA

It should return the following response:

    {"message": "ok", "distance": 3.0265}

Happy geo-coding!


[//]: # (These are reference links)

[OSRM Project]: <http://project-osrm.org/>
