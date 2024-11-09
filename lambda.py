## ---------------------------------------------------------------- ##
# 1.serializeImageData

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Pass the data back to the Step Function
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

## ---------------------------------------------------------------- ##
# 2.classifyImageData

import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-11-06-19-50-00-739"

sagemaker_runtime = boto3.client("sagemaker-runtime")


def lambda_handler(event, context):

    
    # Decode the base64 image data
    image = base64.b64decode(event["image_data"])
    
    # Make a prediction
    # For this model the contentType need to be "image/png"
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="image/png",
        Body=image
    )
    
    # We return the data back to the Step Function   
    inferences = json.loads(response["Body"].read().decode("utf-8"))
    event["inferences"] = inferences
    
    return {
        'statusCode': 200,
        'body': event
    }

## ---------------------------------------------------------------- ##
# 3.filterInferences

import json

THRESHOLD = 0.85

def lambda_handler(event, context):
    
    
    # Grab the inferences from the event
    inferences = event["inferences"]
    
    # Check if any values in our inferences are above the threshold
    meets_threshold = any(infer_value >= THRESHOLD for infer_value in inferences)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }