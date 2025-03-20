import hashlib

def get_hash(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    hash_hex = hash_object.hexdigest()
    hash_int_list = [int(hash_hex[i:i+2], 16) for i in range(0, len(hash_hex), 2)]
    return hash_int_list[:10]