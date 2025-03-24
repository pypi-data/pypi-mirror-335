import importlib.metadata
import base64
import json
import time
from typing import Optional, TypeAlias, Union, Tuple, cast

from lattica_common.app_api import ClientVersionError
from lattica_common.version_utils import get_module_info
import requests
import torch

from lattica_common import http_settings
from lattica_query.serialization.api_serialization_utils import load_proto_tensor, dumps_proto_tensor

ClientPtTensor: TypeAlias = torch.Tensor

"""
IMPLEMENTATION OF API CALLS TO A REMOTE WORKER
every API call should adhere to the following:
api params
    action      the name of the api action
    params      a json struct 

response structure containing either:
    result          the payload execution result
    executionId     the ID of the api call execution when it takes long to
                    return a result 
    error           the execution error
"""

WorkerResponse: TypeAlias = Union[str, dict]


class WorkerHttpClient:
    def __init__(self, query_token: str):
        self.query_token = query_token
        # Determine the module name we're being called from
        self.module_name, self.module_version = get_module_info()

    def _send_http_request(
            self,
            action_name: str,
            action_params: Optional[dict] = None,
            with_polling: Optional[bool] = True
    ) -> Union[None, WorkerResponse]:
        req_data = {
            "api_call": {
                "action": action_name,
                "params": action_params if action_params else {}
            },
            "client_info": {
                "module": self.module_name,
                "version": self.module_version
            }
        }
        req_data.update(http_settings.get_api_body())

        response = requests.post(
            http_settings.get_api_url(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.query_token}'
            },
            json=req_data, verify=False
        )
        if response.ok:
            response_json = json.loads(response.text)
            print(f'{action_name}: {response_json.get("status", "Pending")}')
            
            # Check for version incompatibility error
            if "error" in response_json and "CLIENT_VERSION_INCOMPATIBLE" in response_json.get("error_code", ""):
                raise ClientVersionError(response_json['error'], response_json.get('min_version'))
                
            if "error" in response_json:
                raise Exception(response_json['error'])  # app error
                
            if ("status" in response_json) and (response_json["status"] == "RUNNING") and with_polling:
                return self._resample_result(response_json["executionId"])
                
            if "action_result" in response_json:
                if "error" in response_json["action_result"]:
                    raise Exception(response_json["action_result"]['error'])  # worker error
                return response_json["action_result"]["result"]

        raise Exception(f'FAILED api/{action_name} with error: {response.text}')

    def _resample_result(self, execution_id: str) -> Union[None, WorkerResponse]:
        """Query the status of a previously triggered action."""
        print(f'Polling for executionId: {execution_id}')
        if not execution_id:  # TODO: prevent worker from returning executionId = 0
            return None
        time.sleep(1)
        return self._send_http_request(
            'get_action_result',
            action_params={'executionId': execution_id}
        )


class LatticaWorkerAPI:
    def __init__(self, query_token: str):
        self.http_client = WorkerHttpClient(query_token)

    def get_user_init_data(self) -> Tuple[bytes, bytes]:
        res = cast(dict[str, str], self.http_client._send_http_request('get_user_init_data'))
        return _from_base64(res['context_proto_str']), _from_base64(res['homseq_proto_str'])

    def preprocess_pk(self) -> None:
        self.http_client._send_http_request('preprocess_pk')

    def apply_hom_pipeline(
            self,
            serialized_ct: bytes,
            block_index: int,
            return_new_state: Optional[bool] = False
    ) -> bytes:
        res_proto_str = cast(str, self.http_client._send_http_request(
            'apply_hom_pipeline',
            action_params={
                'ct_proto_str': _to_base64(serialized_ct),
                'block_index': block_index,
                'return_new_state': return_new_state
            }))
        return _from_base64(res_proto_str)

    def apply_clear(self, pt: 'ClientPtTensor') -> 'ClientPtTensor':
        res = self.http_client._send_http_request(
            'apply_clear',
            action_params={'pt_proto_str': _to_serialized_lattica_tensor(pt, as_bytes=False)}
        )
        return _from_serialized_lattica_tensor(res, as_bytes=False)


# ============== start API calls ============== #


def _from_base64(s: str) -> bytes:
    return base64.b64decode(s.encode('utf-8'))


def _to_base64(b: bytes) -> str:
    return base64.b64encode(b).decode('utf-8')


# Format of tensors while they are transmitted through the API

def _to_serialized_lattica_tensor(a, as_bytes=True):
    serialized = dumps_proto_tensor(a, as_bytes=True)
    if as_bytes:
        return serialized
    return _to_base64(serialized)


def _from_serialized_lattica_tensor(a, as_bytes=True):
    if not as_bytes:
        a = _from_base64(a)
    return load_proto_tensor(a, as_bytes=True)
