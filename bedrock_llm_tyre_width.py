import boto3
import json
from botocore.exceptions import ClientError




def validate_tyre_width(tyre_sizes):

    client = boto3.client('bedrock-runtime')
    model_id = "anthropic.claude-v2"

    # Prepare the user message with the required "Human:" prefix and "Assistant:" suffix
   ### Hassan Prompt ##### 
#    user_message = "Human: These are some tyre sizes inserted by the users. It might have some typos or missing information. Return the width from tyre size in mm. If you cannot find width return the value NO_VALID_width. \n" 
#    user_message += "Format of the output should be original input size -> single width(mm). \n" 
    user_message =f"""Human:Extract tire width from complex input formats, prioritizing first numeric sequence matching tire width pattern 
Remove non-numeric characters, performance ratings, extra descriptors (LT, RF, XL, M+S) and for 3 digit input tire size that is width
for irregular formats like "T315/70R17", extract first numeric digits before first / as width 315
Normalize to nearest standard width between 145-375mm: 155, 165, 175, 185, 195, 205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 305, 315, 325, 335, 345, 355, 365, 375
For 3 digit numeric inputs , return both the input number and its nearest standard width, e.g, "456" → 455, "155" → 155,"235"->235 for 3-digit inputs that are already width, return the exact input if between 155-375mm
If you cannot find width return the value NO_VALID_width.
Format of the output should be original input size -> single width(mm). There should be only 1 -> in output width.
"""

    #user_message += "For entries that use * instead of X, treat * as equivalent to X (e.g., 35*12.50R22LT means the width is 12.50 inches, in this case return 35X). \n"
    
    #user_message += "if format of tyre size is wrong return first 3 numeric values before first slash in mm / \n"
    #user_message += "Returned width should be 3 digit and ending with 5 if not in the list return exactly matching or closest value to the list [125, 155, 165, 175, 185, 195, 205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 305, 315, 325, 335, 345, 355, 365, 375, 395] then return 1 closest value of width from the list.\n"
    

   #
   #### Fatima Prompt ####
    #user_message = "Human: Extract the tire width from the provided tire size inputs, the tyre width is usually the first three digit numbers in the standard formats like '315/70R17', where 315 is the width in mm \n"
    #user_message += "Using the given tire width lists: \n"
   # user_message += "Only return tire width in inches if original size contains '×' or '*' and tire widths in inches should be from the list [7, 7.5, 8, 30, 31, 32, 33, 34, 35, 36, 37, 38]  \n"
    #user_message += "Only return tire width in millimeters if original size don't contain  '×' or '*'  should be from the list [125, 155, 165, 175, 185, 195, 205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 305, 315, 325, 335, 345, 355, 365, 375, 395]  \n"
   # user_message += "If tyre format is invalid and contains '/' first 3 numeric digits before '/' is width in mm  \n"
    #user_message += "Evaluate the inputted tire size. If the width directly matches a value in the list, return the matching width. If it does not match, analyze the input and return the closest possible width from the given lists based on standard sizes.  \n"

    #if alpha numeric value or numeric value is present before / return possible 3 digit numeric value e.g. P285/ retrun 285  and for 225/ return 225 similary for all non values give first 3 numeric digits as width in mm \n"
   

    #user_message += "For entries that use *, replace * to X (e.g., 35*12.50R22LT means the width is 35 inches, in this case return 35). \n" 
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
        print (model_output)
        
        # Process the model output to create the dictionary
        result_dict = {}
        for line in model_output.split("\n"):
            if "->" in line:
                original, corrected = line.split("->")
                original = original.strip()
                corrected = [size.strip() for size in corrected.split(",")]
                result_dict[original] = corrected

        print ("dictionary returned")
        print (result_dict)
        return result_dict

    except ClientError as e:
        raise Exception (f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        return None

def get_width_result_as_list(tyre_sizes):
    result_list = []
    result_dict = validate_tyre_width(tyre_sizes)
    print(f"in fun get_result_as_list result_dict is {result_dict}")
    if result_dict is not None:
        print ("entering the result_dict statement")
        for size in tyre_sizes:
            if size in result_dict:
                result_list.append(json.dumps(result_dict[size]))
            else:
                result_list.append(json.dumps(["No value"]))
        print ("return list")
        print (result_list)        
        return result_list
    else :
        print ("else condition result dict")
        for size in tyre_sizes:

         result_list.append(json.dumps(["Error: Model did not return valid results"]))
        print ("return list")
        print (result_list)   
        return result_list    
