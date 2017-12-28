import cv2

vid_cap = cv2.VideoCapture('test.avi')
success, image = vid_cap.read()
count = 0
success = True
while success and count < 1000:
    success, image = vid_cap.read()
    print('Read a new frame: ', success)
    cv2.imwrite("frames/frame%d.png" % count, image)
    count += 1
