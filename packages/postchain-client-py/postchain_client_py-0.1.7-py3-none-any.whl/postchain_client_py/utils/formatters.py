from typing import Any, Dict, Union, List
import binascii
def to_buffer(hex_str: str) -> bytes:
    """Convert hex string to bytes"""
    return binascii.unhexlify(hex_str)

def to_string(buffer: bytes, encoding: str = 'hex') -> str:
    """Convert bytes to string"""
    if encoding == 'hex':
        return binascii.hexlify(buffer).decode('ascii').upper()
    return buffer.decode(encoding)


def to_query_object(name_or_query_object: Union[str, Dict[str, Any]], query_arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convert a query name/arguments or query object into a GTV-compatible format.
    
    Args:
        name_or_query_object: Either a string query name or a query object
        query_arguments: Optional dictionary of query arguments
    
    Returns:
        Dict containing the query in GTV format
    """
    if isinstance(name_or_query_object, str):
        query_object = {"type": name_or_query_object}
        if query_arguments:
            query_object.update(query_arguments)
    else:
        # If it's already a dict, use it directly
        query_object = name_or_query_object
    return query_object