import hashlib

def hash_key(data: str):
    if data == str(''):
        print('Does not contain a valid string')
    
    else:
        new_hash = hashlib.new('sha')
        new_hash.update(data.encode())
        new_key = new_hash.hexdigest()
        
        return new_key

if __name__ == '__main__':
    # Example: qwerty123 -> daaad6e5604e8e17bd9f108d91e26afe6281dac8fda0091040a7a6d7bd9b43b5
    hashes = [
        'daaad6e5604e8e17bd9f108d91e26afe6281dac8fda0091040a7a6d7bd9b43b5', 
        '2fadff0c979214ed48713033fc9d83bbaa0fb7091a665d281f61e07148d97f9b'
    ]
    student_id = ('qwerty123')
    my_key = hash_key(student_id)

    if my_key not in hashes:
        print(f'NEW {my_key}')

        '''
        - Append keys locally or to Sheets
        - Best practice: keep keys in a JSON file
        '''
    
    else:
        print(f'FOUND {my_key}')