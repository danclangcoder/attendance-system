import hashlib

def get_key(data):
    new_hash = hashlib.new('sha256')
    new_hash.update(data.encode())
    new_key = new_hash.hexdigest()
    return new_key

def validate_key(key, my_keys):
    correct_key = True

    if key not in my_keys:
        print('Not found')
        return False
    else:
        return correct_key

if __name__ == '__main__':
    
    # Stored keys indexed on Google Sheets
    my_keys = {
        'bc0cd7c2cebfdde4147fe5c3a517a3c46fdcdd239f2436927f290d317a450d10': {
            'name': 'John Daniel Bandahala',
            'section': 'LAGBSITM91',
            'course': 'BSIT'
        }
    }
    
    while(True):
        key_input = input('Enter\n [1] - Enroll QR\n [2] - scan QR\n [q] - Quit\n')

        if key_input == '1':
            qr_code = input('Scan QR\n')
            new_key = get_key(qr_code)
            my_keys[new_key] = {
                'name': 'New Student',
                'section': '',
                'course': ''
            }

            
                
        # Hash QR using SHA256
        if key_input == '2':
            qr_code = input('Scan QR\n')
            new_key = get_key(qr_code)

            for items in my_keys.values():
                print(items)
            
            print('\n')

            # for key, value in my_keys.items():
            if validate_key(new_key, my_keys) == True:
                info = my_keys[new_key]
                print(f'{info['name']} PRESENT')

        if key_input == 'q':
            break


# Test