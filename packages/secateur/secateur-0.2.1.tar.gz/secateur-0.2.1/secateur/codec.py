from decimal import Decimal
from bson import Decimal128, Binary
from bson.codec_options import CodecOptions, TypeRegistry, TypeCodec
from bson.binary import UuidRepresentation

class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)
    
    def transform_bson(self, value):
        return Decimal(value)
    
class MemoryViewCodec(TypeCodec):
    python_type = memoryview
    bson_type = Binary

    def transform_python(self, value):
        return Binary(value.tobytes())

    def transform_bson(self, value):
        return memoryview(value)

def get_codec_options() -> CodecOptions:    
    type_registry = TypeRegistry(
            [
                DecimalCodec(),
                MemoryViewCodec()
            ]
        )
    
    codec_options = CodecOptions(type_registry=type_registry,
                                 uuid_representation=UuidRepresentation.STANDARD)

    return codec_options
