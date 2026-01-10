import hashlib

def get_key(data):
    new_hash = hashlib.new('sha256')
    new_hash.update(data.encode())
    new_key = new_hash.hexdigest()
    return new_key

def validate_key(key, my_keys):
    correct_key = True

    if key in my_keys:
        return correct_key
    else:
        print('Invalid QR!')

if __name__ == '__main__':
    
    # Stored keys indexed on Google Sheets
    my_keys = {
        'bc0cd7c2cebfdde4147fe5c3a517a3c46fdcdd239f2436927f290d317a450d10': {
            'name': 'John Daniel Bandahala',
            'section': 'LAGBSITM91',
            'course': 'BSIT'
        }
    }

    # Hash QR using SHA256
    qr_code = input('Enter code: ')
    new_key = get_key(qr_code)

    for key, value in my_keys.items():
        if validate_key(new_key, key) == True:
            print(f'{value['name']} PRESENT')