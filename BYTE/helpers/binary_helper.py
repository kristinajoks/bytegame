def bitwise_and_bytes(a, b):
        result_int = int.from_bytes(a, byteorder="big") & int.from_bytes(b, byteorder="big")
        return result_int.to_bytes(max(len(a), len(b)), byteorder="big")
    
def bitwise_or_bytes(a, b):
    result_int = int.from_bytes(a, byteorder="big") | int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")

def bitwise_not_bytes(a):
    result_int = ~ int.from_bytes(a, byteorder="big") + 2 ** (len(a) * 8)
    return result_int.to_bytes(len(a), byteorder="big")