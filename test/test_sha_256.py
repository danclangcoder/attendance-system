import hashlib, test.test_qr_camera as test_qr_camera, test.test_qr_scanner as test_qr_scanner
'''
Generate 256-bit hash values
'''
def create_key(data: str):
    if data == str(''):
        print('Does not contain a valid string')
    
    else:
        new_hash = hashlib.new('sha256')
        new_hash.update(data.encode())
        new_key = new_hash.hexdigest()
        
        return new_key

if __name__ == '__main__':
    qr_code = test_qr_camera.scan_qr()
    # qr_code = qr_scanner.scan_qr()
    qr_key = create_key(qr_code)
    print(qr_code)
    print(len(qr_code))
    print(qr_key)