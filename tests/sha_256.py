import hashlib

def hash_key(data: str):
    if data == str(''):
        print('Does not contain a valid string')
    
    else:
        new_hash = hashlib.new('sha256')
        new_hash.update(data.encode())
        new_key = new_hash.hexdigest()
        
        return new_key

if __name__ == '__main__':
    # student id = qwerty123
    hashes = ['daaad6e5604e8e17bd9f108d91e26afe6281dac8fda0091040a7a6d7bd9b43b5']
    student_id = ('qwerty123')
    my_key = hash_key(student_id)
    print(f'SHA256 -> {my_key}')
    for hash in hashes:
        print(hash == my_key)