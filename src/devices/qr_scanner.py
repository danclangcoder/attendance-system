from serial import Serial

def scan_qr():
    usb = Serial('COM3', baudrate=9600, timeout=0.5)
    
    while usb:
        qr_code = usb.readline().decode()
        if qr_code:
            return qr_code

if __name__ == '__main__':
    qr_code = scan_qr()
    print(qr_code)