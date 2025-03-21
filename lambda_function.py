from typing import Any

from base import BaseAthenaUDF
from pyarrow import Schema
from bedrock_llm_tyre_size import get_result_as_list
from bedrock_llm_tyre_width import get_width_result_as_list
from bedrock_llm_tyre_width_amazon_titan import get_width_result_as_list_amazaon


class SimpleVarcharUDF(BaseAthenaUDF):

    @staticmethod
    def handle_athena_record(input_schema: Schema, output_schema: Schema, arguments: list[Any]):
        print(f"arguments is {arguments}")
        
        process_name = arguments[0][0]
        
        if process_name == 'tyre_size_validation':
            tyre_sizes = [x[1] for x in arguments]
            result = get_result_as_list(tyre_sizes)
            return result

        elif process_name == 'validate_tyre_width':
            tyre_sizes = [x[1] for x in arguments]
            result = get_width_result_as_list(tyre_sizes)
            return result

        elif process_name == 'validate_tyre_width_amazon':
            tyre_sizes = [x[1] for x in arguments]
            result = get_width_result_as_list_amazaon(tyre_sizes)
            return result
            



            
        elif process_name == 'test':
            out = []
            
            for arg in arguments:
                out.append(arg[1].lower())
            return out


# lambda_handler = SimpleVarcharUDF(use_threads=True,chunk_size=1,max_workers=10).lambda_handler
lambda_handler = SimpleVarcharUDF(use_threads=False).lambda_handler
