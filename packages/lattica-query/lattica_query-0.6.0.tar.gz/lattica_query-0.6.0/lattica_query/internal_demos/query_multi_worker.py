import os
import time
import pandas as pd
import torch
import numpy as np

from lattica_common.dev_utils.dev_mod_utils import RUN_MODE, RunMode
from lattica_query.internal_demos.lattica_query_client_local import LocalQueryClient
from lattica_common.internal_demos_common.common_demos_utils import load_e2e_config, print_query_result


print("Starting query client...")

# Load the configuration
_config_path, config = load_e2e_config()

# Typically, 'query_tokens' is a list of tokens for different users
query_tokens = config["query_tokens"]

# Example dataset (MNIST). 
# Adjust the path or load method as needed
dataset = pd.read_csv('data/mnist_data.csv').values / 255.0

for token in query_tokens:
    start_time = time.time()

    # print(f"\n===== Processing Query Token: {token} =====")
    print(f'Running query offline phase for token {token}')
    client = LocalQueryClient(token)

    # OFFLINE PHASE: Generate key (includes retrieving context from worker)
    (
        serialized_context,
        serialized_secret_key,
        serialized_homseq,
    ) = client.generate_key()
    print(f'Initial setup time: {time.time() - start_time}')
    
    # ONLINE PHASE: run queries
    # We'll run 2 random samples for demonstration
    # print("Running homomorphic queries...")
    print(f'Running query online phase for token {token}')

    # Pick a random index
    idx = np.random.randint(len(dataset))
    data_pt = torch.tensor(dataset[idx])
    
    # For debugging: apply pipeline in the clear
    pt_expected = client.apply_clear(data_pt)
    print(f'Image {idx=}')
    pt_dec = client.run_query(serialized_context, serialized_secret_key, data_pt, serialized_homseq)
    print_query_result(idx, data_pt, pt_expected, pt_dec)

print("\nAll queries completed successfully.")
