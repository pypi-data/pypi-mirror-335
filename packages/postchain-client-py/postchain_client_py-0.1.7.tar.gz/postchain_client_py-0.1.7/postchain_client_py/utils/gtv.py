from typing import Dict, List, Union, Any, Tuple
from enum import Enum
import asn1
# Define GTV types
RawGtv = Union[None, bool, bytes, str, int, Dict[str, Any], List[Any]]
DictPairTuple = Tuple[str, Any]
class GTVType(Enum):
    NULL = 0
    BYTE_ARRAY = 1
    STRING = 2
    INTEGER = 3
    DICT = 4
    ARRAY = 5
    BIG_INTEGER = 6
class GTV:
    def __init__(self, type_: GTVType, value: Any):
        self.type = type_
        self.value = value
def gtv_null() -> GTV:
    return GTV(GTVType.NULL, None)
def gtv_bytes(value: bytes) -> GTV:
    return GTV(GTVType.BYTE_ARRAY, value)
def gtv_str(value: str) -> GTV:
    return GTV(GTVType.STRING, value)
def gtv_int(value: int) -> GTV:
    """Convert value to GtvInteger, raises ValueError if out of range"""
    if value > (1 << 63) - 1 or value < -(1 << 63):
        raise ValueError(f"Integer {value} out of range for GtvInteger")
    return GTV(GTVType.INTEGER, value)
def gtv_big_int(value: int) -> GTV:
    """Convert value to GtvBigInteger"""
    return GTV(GTVType.BIG_INTEGER, value)
def gtv_array(values: List[Union[GTV, RawGtv]]) -> GTV:
    typed_values = [
        value if isinstance(value, GTV) else gtv_auto(value) for value in values
    ]
    return GTV(GTVType.ARRAY, typed_values)
def gtv_dict(pairs: Dict[str, Union[GTV, RawGtv]]) -> GTV:
    sorted_pairs = []
    for key, value in sorted(pairs.items()):
        typed_value = value if isinstance(value, GTV) else gtv_auto(value)
        sorted_pairs.append((key, typed_value))
    return GTV(GTVType.DICT, sorted_pairs)
def gtv_auto(value: RawGtv) -> GTV:
    """Convert a Python value to a typed GTV value automatically"""
    if value is None:
        return gtv_null()
    if isinstance(value, bytes):
        return gtv_bytes(value)
    if isinstance(value, bool):
        return gtv_int(1 if value else 0)
    if isinstance(value, str):
        return gtv_str(value)
    if isinstance(value, int):
        try:
            return gtv_int(value)
        except ValueError:
            return gtv_big_int(value)
    if isinstance(value, list):
        return gtv_array(value)
    if isinstance(value, tuple):
        return gtv_array(list(value))
    if isinstance(value, dict):
        return gtv_dict(value)
    raise TypeError(f"Cannot convert type {type(value)} to GTV")

def encode_value(value: Union[RawGtv, GTV]) -> bytes:
    """Encode a value (either RawGTV or already typed GTV) to ASN.1 DER format"""
    encoder = asn1.Encoder()
    encoder.start()
    if isinstance(value, GTV):
        _encode_asn_value(encoder, value)
    else:
        typed_arg = gtv_auto(value)
        _encode_asn_value(encoder, typed_arg)
    return encoder.output()

def _encode_asn_value(encoder: asn1.Encoder, typed_arg: GTV):
    """Helper function to encode GTV values to ASN.1"""
    if typed_arg.type == GTVType.NULL:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            encoder.write(None, asn1.Numbers.Null)
    elif typed_arg.type == GTVType.BYTE_ARRAY:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            encoder.write(typed_arg.value, asn1.Numbers.OctetString)
    elif typed_arg.type == GTVType.STRING:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            encoder.write(typed_arg.value, asn1.Numbers.UTF8String)
    elif typed_arg.type == GTVType.INTEGER:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            encoder.write(typed_arg.value, asn1.Numbers.Integer)
    elif typed_arg.type == GTVType.BIG_INTEGER:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            encoder.write(typed_arg.value, asn1.Numbers.Integer)
    elif typed_arg.type == GTVType.ARRAY:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            with encoder.construct(nr=asn1.Numbers.Sequence):
                for item in typed_arg.value:
                    _encode_asn_value(encoder, item)
    elif typed_arg.type == GTVType.DICT:
        with encoder.construct(nr=typed_arg.type.value, cls=asn1.Classes.Context):
            with encoder.construct(nr=asn1.Numbers.Sequence):
                for key, value in typed_arg.value:
                    with encoder.construct(nr=asn1.Numbers.Sequence):
                        encoder.write(key, asn1.Numbers.UTF8String)
                        _encode_asn_value(encoder, value)
def decode_value(data: bytes) -> GTV:
    """Decode ASN.1 DER format to typed GTV"""
    try:
        decoder = asn1.Decoder()
        decoder.start(data)
        return _decode_typed_value(decoder)
    except Exception as e:
        raise ValueError(f"Failed to decode GTV: {str(e)}")
def decode_raw_value(data: bytes) -> RawGtv:
    """Decode ASN.1 DER format to raw Python value"""
    return to_raw_value(decode_value(data))
def _decode_typed_value(decoder: asn1.Decoder) -> GTV:
    """Helper function to decode ASN.1 to typed GTV"""
    tag = decoder.peek()
    if tag is None:
        return gtv_null()
    tag_nr = tag.nr & ~0xE0  # Remove class bits
    if tag_nr == GTVType.NULL.value:
        decoder.enter()
        decoder.read()
        decoder.leave()
        return gtv_null()
    elif tag_nr == GTVType.BYTE_ARRAY.value:
        decoder.enter()
        _, val = decoder.read()
        decoder.leave()
        return gtv_bytes(val)
    elif tag_nr == GTVType.STRING.value:
        decoder.enter()
        _, val = decoder.read()
        decoder.leave()
        val = val.decode("utf-8") if isinstance(val, bytes) else val
        return gtv_str(val)
    elif tag_nr == GTVType.INTEGER.value:
        decoder.enter()
        _, val = decoder.read()
        decoder.leave()
        return gtv_int(val)
    elif tag_nr == GTVType.BIG_INTEGER.value:
        decoder.enter()
        _, val = decoder.read()
        decoder.leave()
        return gtv_big_int(val)
    elif tag_nr == GTVType.ARRAY.value:
        decoder.enter()
        array = []
        if decoder.peek():
            decoder.enter()  # Enter sequence
            while decoder.peek():
                array.append(_decode_typed_value(decoder))
            decoder.leave()
        decoder.leave()
        return gtv_array(array)
    elif tag_nr == GTVType.DICT.value:
        decoder.enter()
        dict_pairs = {}
        if decoder.peek():
            decoder.enter()  # Enter sequence
            while decoder.peek():
                decoder.enter()  # Enter pair sequence
                _, key = decoder.read()
                key = key.decode("utf-8") if isinstance(key, bytes) else key
                value = _decode_typed_value(decoder)
                dict_pairs[key] = value
                decoder.leave()
            decoder.leave()
        decoder.leave()
        return gtv_dict(dict_pairs)
    raise ValueError(f"Unexpected ASN.1 tag: {tag}")
def to_raw_value(gtv: GTV) -> RawGtv:
    """Convert typed GTV to raw Python value"""
    if gtv.type == GTVType.NULL:
        return None
    elif gtv.type in (
        GTVType.BYTE_ARRAY,
        GTVType.STRING,
        GTVType.INTEGER,
        GTVType.BIG_INTEGER,
    ):
        return gtv.value
    elif gtv.type == GTVType.ARRAY:
        return [to_raw_value(x) for x in gtv.value]
    elif gtv.type == GTVType.DICT:
        return {k: to_raw_value(v) for k, v in gtv.value}
    else:
        raise TypeError(f"Unknown GTV type: {gtv.type}")
def is_gtv_compatible(value: Any) -> bool:
    """Check if a value can be represented in GTV automatically"""
    try:
        gtv_auto(value)
        return True
    except TypeError:
        return False