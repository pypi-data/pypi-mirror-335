import time
import os

from lattica_query import worker_api
from timeit_decorator import timeit

from typing import TYPE_CHECKING, Tuple

from lattica_common.app_api import LatticaAppAPI
from lattica_query.worker_api import LatticaWorkerAPI
import lattica_query.query_toolkit as toolkit_interface

from lattica_query.serialization.hom_op_pb2 import (
    QueryClientSequentialHomOp as ProtoQueryClientSequentialHomOp,
)


if TYPE_CHECKING:
    from lattica_query.worker_api import ClientPtTensor


class QueryClient:
    """
    A simple client to demonstrate how to:
      - Retrieve user init data (context, homseq) from worker
      - Generate local keys (secret_key, public_key)
      - Upload the public key file to Lattica
      - Preprocess the public key on the worker
      - Run multiple queries homomorphically (comparing with clear)
    """

    def __init__(self, query_token: str):
        """
        Initialize the QueryClient with a user (query) token.
        """
        self.query_token = query_token
        self.agent_app = LatticaAppAPI(self.query_token)
        self.worker_api = LatticaWorkerAPI(self.query_token)

    def generate_key(self) -> Tuple[bytes, Tuple[bytes, bytes], bytes]:
        """
        - Retrieve context/hom-sequence from the worker.
        - Generate the local FHE key pair (secret_key, public_key).
        - Upload public key

        Returns:
            (serialized_context, serialized_secret_key, serialized_homseq)
        """
        print("Retrieving user init data (context, homseq) from worker...")
        serialized_context, serialized_homseq = self.worker_api.get_user_init_data()

        print("Creating client FHE keys...")
        serialized_secret_key, serialized_public_key = toolkit_interface.generate_key(
            serialized_homseq,
            serialized_context
        )

        print(f'Registering FHE public key...')
        temp_filename = 'my_pk.lpk'
        with open(temp_filename, 'wb') as handle:
            handle.write(serialized_public_key)

        self.upload_public_key_file(temp_filename)
        os.remove(temp_filename)

        return (
            serialized_context,
            serialized_secret_key,
            serialized_homseq,
        )

    def apply_clear(self, data_pt):
        return self.worker_api.apply_clear(data_pt)

    def upload_public_key_file(self, pk_filename: str) -> None:
        """
        Upload the user's public key file to the Lattica server,
        alert the server that upload completed, and then have the worker
        preprocess the key.
        """
        print(f"Uploading public key file '{pk_filename}' to server...")
        file_key = self.agent_app.upload_user_file(pk_filename)

        alert_upload_complete = self.agent_app.alert_upload_complete(file_key)
        print(f"pk {pk_filename} uploaded status is {alert_upload_complete}.")

        # Instruct the worker to preprocess the newly uploaded public key
        print(f'Calling to preprocess {pk_filename}')
        self.worker_api.preprocess_pk()
        print("Public key preprocessing on worker is complete.")
        return

    @timeit(log_level=None)
    def run_query(self,
                    serialized_context: bytes,
                    serialized_sk: tuple[bytes, bytes],
                    pt: 'ClientPtTensor',
                    serialized_homseq: bytes
                    ) -> 'ClientPtTensor':
        client_time = 0
        be_time = 0

        start = time.perf_counter()
        serialized_pt = worker_api._to_serialized_lattica_tensor(pt)
        homsec_proto = ProtoQueryClientSequentialHomOp()
        homsec_proto.ParseFromString(serialized_homseq)
        client_blocks_proto = homsec_proto.client_blocks

        is_be_first = len(client_blocks_proto) == 0 or client_blocks_proto[0].block_index != 0
        client_time += time.perf_counter() - start

        if is_be_first:
            start = time.perf_counter()
            serialized_ct = toolkit_interface.enc(
                serialized_context, serialized_sk, serialized_pt, pack_for_transmission=True)
            client_time += time.perf_counter() - start
            start = time.perf_counter()
            serialized_ct_res = self.worker_api.apply_hom_pipeline(
                serialized_ct, block_index=0)
            be_time += time.perf_counter() - start
            start = time.perf_counter()
            serialized_pt = toolkit_interface.dec(serialized_context, serialized_sk, serialized_ct_res)
            client_time += time.perf_counter() - start

        for block_proto in client_blocks_proto:
            start = time.perf_counter()
            print(f'Applying client operators')
            serialized_block_proto = block_proto.SerializeToString()
            serialized_pt = toolkit_interface.apply_client_block(
                serialized_block_proto, serialized_context, serialized_pt)
            if block_proto.is_last:
                break

            pt_axis_external = block_proto.pt_axis_external if block_proto.HasField("pt_axis_external") else None
            serialized_ct = toolkit_interface.enc(
                serialized_context, serialized_sk, serialized_pt, pack_for_transmission=True, n_axis_external=pt_axis_external)
            client_time += time.perf_counter() - start
            start = time.perf_counter()
            serialized_ct_res = self.worker_api.apply_hom_pipeline(
                serialized_ct, block_index=block_proto.block_index+1)
            be_time += time.perf_counter() - start
            start = time.perf_counter()
            serialized_pt = toolkit_interface.dec(serialized_context, serialized_sk, serialized_ct_res)
            client_time += time.perf_counter() - start

        print(f'=================== Client time: {client_time} BE time: {be_time} ===================')
        return worker_api._from_serialized_lattica_tensor(serialized_pt)
