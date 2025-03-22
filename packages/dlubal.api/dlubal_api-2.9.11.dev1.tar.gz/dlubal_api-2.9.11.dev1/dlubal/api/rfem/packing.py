from dlubal.api.rfem.application_pb2 import Object, ObjectList, CreateObjectListRequest
from dlubal.api.common.table import Table
from dlubal.api.common.table_data_pb2 import TableData
from google.protobuf.any_pb2 import Any
from google.protobuf.struct_pb2 import Value
import pandas as pd
from pandas import DataFrame


def pack_object(object, model_id=None) -> Object:
    packed = Any()
    packed.Pack(object)

    if model_id is None:
        return Object(object=packed)

    return Object(object=packed, model_id=model_id)


def unpack_object(packed_object: Object, Type):
    result = Type()
    packed_object.object.Unpack(result)
    return result


def pack_object_list(object_list, model_id=None, return_object_id=None):
    packed_list = ObjectList()
    packed_list.objects.extend(pack_object(obj, model_id) for obj in object_list)

    if return_object_id is not None:
        return CreateObjectListRequest(objects=packed_list, return_object_id=return_object_id)

    return packed_list


def unpack_object_list(packed_object_list: ObjectList, type_lst: list):
    unpacked_list = []

    for i, object in enumerate(packed_object_list.objects):
        unpacked_list.append(unpack_object(object, type_lst[i]))

    return unpacked_list


def get_internal_value(value: Value):
    '''
    Get the internal value stored in a generic Value object
    '''
    kind = value.WhichOneof("kind")
    if kind == "null_value":
        return None
    else:
        return getattr(value, kind)


def convert_table_data_to_table(table_data: TableData) -> Table:
    '''
    Converts TableData from API response to a Pandas-based Table.

    Args:
        table_data (TableData): Raw API response in TableData format.

    Returns:
        Table: Converted table with appropriate data types.
    '''
    rows_data = [
        [pd.NA if (value := get_internal_value(v)) is None else value for v in row.values]
        for row in table_data.rows
    ]

    df = DataFrame(columns=list(table_data.column_ids), data=rows_data)

    # Convert DataFrame columns to their best possible numeric nullable dtypes.
    df_conv = df.convert_dtypes()

    # Ensure float columns remain float, even if they contain only whole numbers
    float_cols = df.select_dtypes(include=["float"]).columns
    df_conv[float_cols] = df_conv[float_cols].astype('Float64')

    # Convert non-numeric object type columns to Pandas' nullable string type.
    object_cols = df_conv.select_dtypes(include=["object"]).columns
    df_conv[object_cols] = df_conv[object_cols].astype('string')

    return Table(df_conv)
