import boto3
import json
from botocore.exceptions import ClientError


def validate_tyre_width_amazon_titan(tyre_sizes):

    user_message = "Human: These are some tyre sizes inserted by the users. It might have some typos or missing information. Return tyre width in mm.  \n" 
    user_message += "Format should be original size -> width (mm). \n" 
    user_message += "\n".join(tyre_sizes)
    user_message += "\nAssistant:"
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Set the model ID, e.g., Titan Text Premier.
    model_id = "amazon.titan-text-premier-v1:0"

    # Define the prompt for the model.

    # Format the request payload using the model's native structure.
    native_request = {
    "inputText": user_message,
    "textGenerationConfig": {
        "maxTokenCount": 512,
        "temperature": 0.5,
        },
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
    # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    
    # Decode the response body.
        model_response = json.loads(response["body"].read())

        model_output = response_body['completion']
        print("Got response from LLM ....")
        
            # Process the model output to create the dictionary
        result_dict = {}
        for line in model_output.split("\n"):
            if "->" in line:
                original, corrected = line.split("->")
                original = original.strip()
                corrected = [size.strip() for size in corrected.split(",")]
                result_dict[original] = corrected

        return result_dict

    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

def get_width_result_as_list_amazaon(tyre_sizes):
    result_list = []
    result_dict = validate_tyre_width_amazon_titan(tyre_sizes)
    print(f"in fun get_result_as_list result_dict is {result_dict}")
    for size in tyre_sizes:
        if size in result_dict:
            result_list.append(json.dumps(result_dict[size]))
        else:
            result_list.append(json.dumps(["No value"]))
    return result_list
