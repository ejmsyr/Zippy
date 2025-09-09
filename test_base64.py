import base64
import zlib

original_string = "1234567890abcdefghijklmnopqrstuvwxyz"

# Encoding
compressed_bytes = zlib.compress(original_string.encode('utf-8'))
encoded_bytes = base64.urlsafe_b64encode(compressed_bytes)
encoded_string = encoded_bytes.decode('utf-8')

print(f"Original string: {original_string}")
print(f"Encoded string: {encoded_string}")

# Decoding
decoded_bytes = base64.urlsafe_b64decode(encoded_string.encode('utf-8'))
decompressed_bytes = zlib.decompress(decoded_bytes)
decoded_string = decompressed_bytes.decode('utf-8')

print(f"Decoded string: {decoded_string}")

assert original_string == decoded_string
print("Success!")