from typing import TYPE_CHECKING, Union

from lattica_query.serialization import serialization_utils


def load_proto_tensor(data: Union[str, bytes], as_bytes=False) -> 'Tensor':
    if not as_bytes:
        data = eval(data)
    return serialization_utils.deser_tensor_raw(data, as_str=True)


def dumps_proto_tensor(data: 'Tensor', as_bytes=False) -> Union[str, bytes]:
    res_bytes = serialization_utils.ser_tensor(data).SerializeToString()
    if as_bytes:
        return res_bytes
    return str(res_bytes)
