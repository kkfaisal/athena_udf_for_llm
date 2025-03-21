import base64
from typing import Any, Optional
from uuid import uuid4

import pyarrow as pa

from utils import process_records, process_records_in_chunks


class BaseAthenaUDF:

    def __init__(self, chunk_size: Optional[int] = None, use_threads: bool = True, max_workers: Optional[int] = None):
        self.chunk_size = chunk_size
        self.use_threads = use_threads
        self.max_workers = max_workers

    @staticmethod
    def handle_ping(event):
        return {
            "@type": "PingResponse",
            "catalogName": "event",
            "queryId": event["queryId"],
            "sourceType": "athena_udf",
            "capabilities": 23,
        }

    def lambda_handler(self, event, context):
        incoming_type = event["@type"]
        if incoming_type == "PingRequest":
            return self.handle_ping(event)
        elif incoming_type == "UserDefinedFunctionRequest":
            return self.handle_udf_request(event)

        raise Exception(f"Unknown event type {incoming_type} from Athena")

    def handle_udf_request(self, event):
        input_schema = pa.ipc.read_schema(pa.BufferReader(base64.b64decode(event["inputRecords"]["schema"])))
        output_schema = pa.ipc.read_schema(pa.BufferReader(base64.b64decode(event["outputSchema"]["schema"])))
        record_batch = pa.ipc.read_record_batch(
            pa.BufferReader(base64.b64decode(event["inputRecords"]["records"])),
            input_schema,
        )
        
        # record_batch_list = record_batch.to_pylist()
        
        record_batch_single_list = record_batch.to_pylist()
        record_batch_single_list =[list(x.values()) for x in record_batch_single_list ]
        
        chunk_size = 500
        record_batch_list = [record_batch_single_list[i:i + chunk_size] for i in range(0, len(record_batch_single_list), chunk_size)]

        if self.use_threads:
            if self.chunk_size is None:
                outputs_array = process_records(
                    self.handle_athena_record, (input_schema, output_schema), record_batch_list, self.max_workers
                )
                outputs = [item for sublist in outputs_array for item in sublist]
            else:
                outputs_array = process_records_in_chunks(
                    self.handle_athena_record,
                    (input_schema, output_schema),
                    record_batch_list,
                    self.chunk_size,
                    self.max_workers,
                )
                outputs = [item for sublist in outputs_array for item in sublist]
        else:
            outputs_array = [
                self.handle_athena_record(input_schema, output_schema, record) # list(record.values())
                for record in record_batch_list
            ]
            
            print(f"outputs_array {outputs_array}")
            outputs = [item for sublist in outputs_array for item in sublist]
            print(f"outputs is {outputs}")
            
        return {
            "@type": "UserDefinedFunctionResponse",
            "records": {
                "aId": str(uuid4()),
                "schema": event["outputSchema"]["schema"],
                "records": base64.b64encode(
                    pa.RecordBatch.from_arrays([outputs], schema=output_schema).serialize()
                ).decode(),
            },
            "methodName": event["methodName"],
        }

    @staticmethod
    def handle_athena_record(input_schema: pa.Schema, output_schema: pa.Schema, arguments: list[Any]):
        raise NotImplementedError()