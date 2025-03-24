from lattica_query.internal_demos.lattica_query_client_local import LocalQueryClient
from lattica_common.internal_demos_common.common_demos_utils import print_query_result
from lattica_query.worker_api import LatticaWorkerAPI
import torch

import lattica_query.hom_common as hom_common


# TODO (pavel): this script is not up to date and won't work!
worker_api_client = LatticaWorkerAPI("<YOUR-TOKEN-HERE>")
query_client = LocalQueryClient("<YOUR-TOKEN-HERE>")

# or you can pass the token as an arg to `get_context':
serialized_context, serialized_homseq = worker_api_client.get_user_init_data()

print('Loading local secret key...')
serialized_sk = hom_common.read_byte_arrays_from_file('my_secret_key.lsk')

for i in range(5):
    print(f'Iteration {i=}')

    # create a plaintext tensor with the correct shape
    data_pt = torch.rand(10, dtype=torch.float64)

    pt_expected = query_client.apply_clear(data_pt)
    print(f'Image {i=}')
    pt_dec = query_client.run_query(serialized_context, serialized_sk, data_pt, serialized_homseq)
    print_query_result(i, data_pt, pt_expected, pt_dec)
