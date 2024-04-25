import boto3
import json
import base64
from botocore.exceptions import ClientError, ValidationError

LLM_SERVICE_ENDPOINT_ADDRESS = f"text-vision-llm-model-7B-image2text"

PROMPT = """
You will be provided with an image of a pdf page or a slide. Your goal is to talk about the content that you see, in technical terms, as if you were delivering a presentation.

If there are diagrams, describe the diagrams and explain their meaning.
For example: if there is a diagram describing a process flow, say something like "the process flow starts with X then we have Y and Z..."

If there are tables, describe logically the content in the tables
For example: if there is a table listing items and prices, say something like "the prices are the following: A for X, B for Y..."

DO NOT include terms referring to the content format
DO NOT mention the content type - DO focus on the content itself
For example: if there is a diagram/chart and text on the image, talk about both without mentioning that one is a chart and the other is text.
Simply describe what you see in the diagram and what you understand from the text.

You should keep it concise, but keep in mind your audience cannot see the image so be exhaustive in describing the content.

Exclude elements that are not relevant to the content:
DO NOT mention page numbers or the position of the elements on the image.
"""
TEXT = f'<ImageHere>{PROMPT}'

with open("calendar.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    base64_string = encoded_string.decode('utf-8')
    print(base64_string)

def call_sagemaker(prompt, image_base64, endpoint_name=LLM_SERVICE_ENDPOINT_ADDRESS):
    print("Prompt")
    print(prompt)
    payload = {
        "inputs": [
            [
                {"role": "user", "content": str(prompt), "image": image_base64}
            ]
        ],
        "parameters": {
            "max_tokens": 1024,
            "top_p": 0.8,
            "temperature": 1.0,
            "repeat_penalty": 1.005
        }
    }

    sagemaker_client = boto3.client("sagemaker-runtime")
    payload = json.dumps(payload)
    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=payload
    )
    response_string = response["Body"].read().decode()
    return response_string

response = call_sagemaker(prompt=TEXT, image_base64=base64_string)
json_resposne = json.loads(response)

print(json_resposne)