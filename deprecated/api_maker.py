import secrets

def generate_api_key():
    # This generates a 32-character hexadecimal token.
    return secrets.token_hex(16)

api_key = generate_api_key()
print("Your generated API key:", api_key)
