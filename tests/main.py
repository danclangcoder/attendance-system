from time import sleep
from datetime import datetime
from qr_scanner import scan_qr
from sha_256 import hash_key

if __name__ == '__main__':
    print('Running app... Please wait.')
    sleep(1)
    print('Scan QR')
    while True:
        try:
            qr = scan_qr()
            hash_val = hash_key(qr)
            current_time = datetime.now().strftime('%I:%M %p')
            print(current_time)

        except KeyboardInterrupt:
            break