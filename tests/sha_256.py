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
    students = {
        "A123F0024": "bc0cd7c2cebfdde4147fe5c3a517a3c46fdcdd239f2436927f290d317a450d10"
    }
    
    in_menu = True

    while in_menu:
        char = input('Enter to REGISTER and q or Q to QUIT: ')
        if char == 'q' or 'Q':
            break

        student_number = input('Enter Student No: ')
        new_hash = hash_key(student_number)

        if new_hash not in students.values():
            print(f'NEW {new_hash}')
            students[student_number] = new_hash
        
        else:
            print(f'FOUND {new_hash}')