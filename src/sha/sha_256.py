import hashlib
'''
Generate 256-bit hash values
'''
def create_key(qr: str) -> str:
    if qr == '':
        raise ValueError('Does not contain a valid string.')
    else:
        new_hash = hashlib.new('sha256')
        new_hash.update(qr.encode())
        new_key = new_hash.hexdigest()
        return new_key

if __name__ == '__main__':
    ...