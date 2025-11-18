import base64
import hashlib
import hmac
import time
import random

from datetime import datetime, timezone

from sell.models import IpcLog


def base32_decode2(encoded):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    encoded = encoded.upper()
    bits = ''
    for char in encoded:
        bits += bin(alphabet.index(char))[2:].zfill(5)
    decoded = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return decoded


def base32_decode(encoded):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    encoded = encoded.upper()
    bits = ''
    for char in encoded:
        if char in alphabet:
            index = alphabet.index(char)
        else:
            index = 0
        bits += bin(index)[2:].zfill(5)
    decoded = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8) if len(bits[i:i + 8]) == 8)
    return decoded


def hotp(key, counter, digits=6):
    counter_bytes = counter.to_bytes(8, 'big')
    hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0xf
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff))
    code %= 10 ** digits
    return str(code).zfill(digits)


def totp(key, time_step=30, digits=6):
    time_counter = int(time.time() / time_step)
    dt_now = datetime.now(timezone.utc)
    timestamp = datetime.timestamp(dt_now)
    time_counter = int(timestamp / time_step)
    return hotp(key, time_counter, digits)


def encode(input_str, key, _count):
    enc = ''
    for i in range(len(input_str)):
        digit = int(input_str[i])
        k = int(key[i])
        enc += str((digit + k) % 10)

    positions = list(range(0, _count))
    hash_part = hashlib.md5(key[6:10].encode()).hexdigest()
    positions.sort(key=lambda x: ord(hash_part[x % 32]))

    final_code = ''
    for pos in positions:
        final_code += enc[pos]
    return final_code


def generateotp(_gsid, _nid):
    try:


        secret = 'BSTDMNH056TRL9HS'
        decoded_secret = base32_decode(secret)
    except:

        secret = 'BSTDMNH056TRL9HS'
        decoded_secret = base32_decode(secret)

    # decoded_secret = base32_decode(secret)

    GSID = str(_gsid)
    NID = str(_nid)
    otp_code = totp(decoded_secret, 600, 5)

    combined = GSID + NID + otp_code

    key = otp_code + otp_code[2] + GSID + '1'
    final_code = GSID + NID + otp_code
    enc = encode(final_code, key, 11)
    return enc





    shuffle_key = '1450'
    hash = hashlib.md5(shuffle_key.encode()).hexdigest()
    positions = list(range(11))
    positions.sort(key=lambda x: ord(hash[x % 32]))

    final_code = ''.join(combined[pos] for pos in positions)

    # print("The current combined code is:", final_code)

    received_final_code = final_code

    decoded_combined = [''] * 11
    for index, pos in enumerate(positions):
        decoded_combined[pos] = received_final_code[index]
    decoded_combined = ''.join(decoded_combined)

    decoded_GSID = decoded_combined[:4]
    decoded_NID = decoded_combined[4:6]
    decoded_otp_code = decoded_combined[6:]

    # if totp(decoded_secret, 300, 5) == decoded_otp_code:
    #     print("The OTP is valid!")
    # else:
    #     print("The OTP is invalid!")
    return final_code
