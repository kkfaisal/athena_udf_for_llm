import boto3
import json
from botocore.exceptions import ClientError


def validate_tyre_sizes(tyre_sizes):

    client = boto3.client('bedrock-runtime')
    model_id = "anthropic.claude-v2"

    # Prepare the user message with the required "Human:" prefix and "Assistant:" suffix
    user_message = "Human: These are some tyre sizes inserted by the users. It might have some typos or missing information. Please send back corrected sizes.\n"
    user_message += "Format should be original size -> corrected size1, corrected size2, corrected size3. Include more options if needed.If no correction eeded specify that.If it is totally invalid also specify that \n"
    user_message += "\n".join(tyre_sizes)
    user_message += "\nAssistant:"

    try:
        # Send the message to the Bedrock LLM model
        print("Called LLM invoke...")
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            body=json.dumps({
                "prompt": user_message,
                "max_tokens_to_sample": 2500
            })
        )

        # Read the response
        response_body = json.loads(response['body'].read())
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

def get_result_as_list(tyre_sizes):
    result_list = []
    result_dict = validate_tyre_sizes(tyre_sizes)
    print(f"in fun get_result_as_list result_dict is {result_dict}")
    for size in tyre_sizes:
        if size in result_dict:
            result_list.append(json.dumps(result_dict[size]))
        else:
            result_list.append(json.dumps(["No value"]))
    return result_list