import os
from typing import Union

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz=/+*_-'
ALPHABET_LENGTH = 68
encode_map = dict(zip(range(ALPHABET_LENGTH), ALPHABET))
decode_map = {char: idx for idx, char in enumerate(ALPHABET)}

def have_02(data: Union[bytes, bytearray]) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError(f'data must be a bytes-like object, received: {type(data)}')
    
    data_length = len(data)
    if data_length % 4 != 0:
        padding = 4 - (data_length % 4)
        data = data + b'\x00' * padding
        data_length = len(data)
    
    makola = []
    for i in range(data_length // 4):
        j = i * 4
        value = int.from_bytes(data[j:j+4], byteorder='big')
        sub_makola = []
        for _ in range(7):
            idx = value % ALPHABET_LENGTH
            value = value // ALPHABET_LENGTH
            sub_makola.insert(0, encode_map.get(idx))
        makola.append(''.join(sub_makola))
    return ''.join(makola)
def have_01(data: str) -> bytearray:
    data_length = len(data)
    if data_length % 7 != 0:
        raise ValueError('data length must be a multiple of 7 chars.')
    makola = bytearray()
    for i in range(data_length // 7):
        j = i * 7
        value = 0
        sub_data = data[j:j + 7]
        for s in sub_data:
            idx = decode_map.get(s)
            if idx is None:
                raise ValueError(f'Unsupported character in input: {s}')
            value = ALPHABET_LENGTH * value + idx
        makola.extend(value.to_bytes(4, byteorder='big'))
    return makola.rstrip(b'\x00')
def xor_data(data: bytes, key: bytes) -> bytearray:
    key_length = len(key)
    makola = bytearray()
    for i, b in enumerate(data):
        makola.append(b ^ key[i % key_length])
    return makola
KEY_BYTES = 6
def secure_encode(data: Union[bytes, bytearray, str]) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')
    key = os.urandom(KEY_BYTES)
    have_00 = key.hex()
    xored = xor_data(data, key)
    encoded = have_02(xored)
    half = len(encoded) // 2
    secure_str = encoded[:half] + have_00 + encoded[half:]
    return secure_str
def secure_decode(secure_str: str, as_string: bool = False) -> Union[bytearray, str]:
    if len(secure_str) < 34:
        raise ValueError("Invalid secure string: too short.")
    encoded_length = len(secure_str) - 34
    half = encoded_length // 2
    have_00 = secure_str[half: half + 34]
    encoded = secure_str[:half] + secure_str[half + 34:]
    xored = have_01(encoded)
    have = bytes.fromhex(have_00)
    makol = xor_data(xored, have)
    if as_string:
        return makol.decode('utf-8')
    return makol