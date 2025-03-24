import json
import base64

from lattica_query import cpp_sdk



def generate_key(
        serialized_homseq: bytes,
        serialized_context: bytes,
) -> tuple[tuple[bytes, bytes], bytes]:

    res = cpp_sdk.generate_key(
        serialized_homseq, serialized_context
    )
    return res


def enc(
        serialized_context: bytes,
        serialized_sk: tuple[bytes, bytes],
        serialized_pt: bytes,
        pack_for_transmission: bool = False,
        n_axis_external: int = None
) -> bytes:

    ct_proto_bytes = cpp_sdk.enc(
        serialized_context,
        serialized_sk[0],
        serialized_pt,
        pack_for_transmission,
        n_axis_external
    )
    return ct_proto_bytes



def dec(
        serialized_context: bytes,
        serialized_sk: tuple[bytes, bytes],
        serialized_ct: bytes,
) -> bytes:

    res = cpp_sdk.dec(
        serialized_context,
        serialized_sk[1],
        serialized_ct
    )
    return res



def apply_client_block(
        serialized_block: bytes,
        serialized_context: bytes,
        serialized_pt: bytes
) -> bytes:

    res = cpp_sdk.apply_client_block(
        serialized_block, serialized_context, serialized_pt
    )
    return res

