'''
    Docstring for tests.__main__

    Put test code here, not in src.
'''

import cv2, time
from pyzbar.pyzbar import decode


def run_app():
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Width and Height of the app window
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    camera_open = True

    # Empty list for storing QR to prevent continouos process and crashing
    scanned_codes = []

    print('Scan your QR')
    while camera_open:
        success, frame = cam.read()

        if not success:
            print('Camera device not selected.')
            break

        for output in decode(frame):
            str_txt = output.data.decode('utf-8')

            if str_txt in scanned_codes:
                print('Already scanned today')
                time.sleep(5)
            else:
                print(str_txt)
                time.sleep(1)
                scanned_codes.append(str_txt)
                

        window_name = 'QR Scanner'
        cv2.imshow(window_name, cv2.flip(frame, 1))
        key_press = cv2.waitKey(1)
        esc_key = chr(27)
        
        if key_press == ord(esc_key):
            break

        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cam.release()   
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print('Running app... Please wait.')
    run_app()