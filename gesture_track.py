import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import time
import requests
import math


""" we need:
 1. real-time video capture
 2. background blur (removal)
 3. template matching
 4. Skin color detection
 5. tracking the position and orientation of moving objects

 """

## helper function for reading the images, returns the dimensions of the image using ".shape"
def read_img(path):   
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED) 
    print('Original Dimensions : ',img.shape)
    return img


## helper function for resizing the image, scaled by the percentage
def make_frame_smaller(frame,ratio):
    # get size from a matrix
    height = frame.shape[0]
    width = frame.shape[1]
    #resize using cv2.resize(...)
    result = cv2.resize(frame,(int(width*ratio),int(height*ratio)))
    return result


## converting image into grayscaled image
def gray_img(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img

# def background_removal(frame):
#     #iterate each pixel in a frame
#     for i in range(frame.shape[0]):
#         for j in range(frame.shape[1]):
#             b,g,r = frame[i][j]
#             #for red color pixel:
#             if (r > 150 and b < 100 and g < 100):
#                 #white
#                 frame[i][j][0] = 255
#                 frame[i][j][1] = 255
#                 frame[i][j][2] = 255
#             else:
#                 #black
#                 frame[i][j][0] = 0
#                 frame[i][j][1] = 0
#                 frame[i][j][2] = 0
#     return frame



# def skin_detect(img):

#     image = img.copy()  ## getting a copy of an image input
    
#     ## converting from BGR to HSV color space
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     # bound of skin color	try : [0, 58, 30], [33, 255, 255]
#     # min_bound = np.array([0, 58, 30], dtype=np.uint8)
#     # max_bound = np.array([33, 255, 255], dtype=np.uint8)
#     min_bound = np.array([0, 48, 80], dtype=np.uint8)
#     max_bound = np.array([20, 255, 255], dtype=np.uint8)
#     # skin color mask
#     mask_skin = cv2.inRange(image, min_bound, max_bound)
#     # using threshold mask to extract skin color
#     skin_img = cv2.bitwise_and(image, image, mask = mask_skin)
#     # return the skin detection image
#     return cv2.cvtColor(skin_img, cv2.COLOR_HSV2BGR)


def template_matching(frame,templates,original,time1, old_xleft, old_ytop):
    diff_time = time.time() - time1
    #convert them to grayscale
    # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    pause = templates[0]
    play = templates[1]
    uni_gesture = templates[2]

    pause = cv2.cvtColor(pause,cv2.COLOR_BGR2GRAY)
    play = cv2.cvtColor(play,cv2.COLOR_BGR2GRAY)
    uni_gesture = cv2.cvtColor(uni_gesture,cv2.COLOR_BGR2GRAY)
    
    (templateWP, templateHP) = pause.shape
    (templateWS, templateHS) = play.shape
    (templateWR, templateHR) = uni_gesture.shape

    #template matching
    resP = cv2.matchTemplate(frame,pause,cv2.TM_CCOEFF_NORMED)
    resS = cv2.matchTemplate(frame,play,cv2.TM_CCOEFF_NORMED)
    resR = cv2.matchTemplate(frame,uni_gesture,cv2.TM_CCOEFF_NORMED)
    
    #get the position of recognized object
    min_valP, max_valP, min_locP, max_locP = cv2.minMaxLoc(resP)
    min_valS, max_valS, min_locS, max_locS = cv2.minMaxLoc(resS)
    min_valR, max_valR, min_locR, max_locR = cv2.minMaxLoc(resR)

    scores = [max_valP, max_valS, max_valR]
    best_score = max(scores)
    xleft = 0
    ytop = 0
    speed_threshold = 500
    if best_score > 0.60:

        # if best match is pause
        if best_score == max_valP:
            xleftP,ytopP = max_locP
            bottom_rightP = (xleftP + templateWP, ytopP + templateHP)

            #draw a green bounding box on the original image for visualization. 
            cv2.rectangle(original,(xleftP,ytopP), bottom_rightP, (0,255,0), 2)
            cv2.putText(original,'Pause ' + str(best_score),(xleftP,ytopP),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            if best_score > 0.80:
                xml = """<key state="press" sender="Gabbo">PAUSE</key>"""
                headers = {'Content-Type': 'application/xml'}
                requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            
            speed1 = abs(xleftP - old_xleft)/diff_time
            # check speed
            # if speed1 > speed_threshold:
            #     if xleftP-old_xleft > 120:
            #         cv2.putText(original,'Last song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            #         xml = """<key state="press" sender="Gabbo">PREV_TRACK</key>"""
            #         headers = {'Content-Type': 'application/xml'}
            #         requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            #     elif xleftP-old_xleft < 120:
            #         cv2.putText(original,'Next song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            #         xml = """<key state="press" sender="Gabbo">NEXT_TRACK</key>"""
            #         headers = {'Content-Type': 'application/xml'}
            #         requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            xleft = xleftP
            ytop = ytopP

        # if best match is play
        elif best_score == max_valS:
            xleftS,ytopS = max_locS
            bottom_rightS = (xleftS + templateWS, ytopS + templateHS)
        
            #draw a blue bounding box on the original image for visualization. 
            cv2.rectangle(original,(xleftS,ytopS), bottom_rightS, (255,0,0), 2)
            cv2.putText(original,"Play " + str(best_score),(xleftS,ytopS),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            
            if best_score > 0.80:
                xml = """<key state="press" sender="Gabbo">PLAY</key>"""
                headers = {'Content-Type': 'application/xml'}
                requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text

            # speed1 = abs(xleftS - old_xleft)/diff_time
            # if speed1 > speed_threshold:
            #     if xleftS-old_xleft > 120:
            #         cv2.putText(original,'Last song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            #         xml = """<key state="press" sender="Gabbo">PREV_TRACK</key>"""
            #         headers = {'Content-Type': 'application/xml'}
            #         requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            #     elif xleftS-old_xleft < 120:
            #         cv2.putText(original,'Next song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            #         xml = """<key state="press" sender="Gabbo">NEXT_TRACK</key>"""
            #         headers = {'Content-Type': 'application/xml'}
            #         requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            xleft = xleftS
            ytop = ytopS
            
        else: # if best match is uni_gesture
            xleftR,ytopR = max_locR
            bottom_rightR = (xleftR + templateWR, ytopR + templateHR)
            #draw a red bounding box on the original image for visualization. 
            cv2.rectangle(original,(xleftR,ytopR), bottom_rightR, (0,0,255), 2)
            cv2.putText(original,"Uni_Gesture " + str(best_score),(xleftR,ytopR),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
            speed1 = abs(xleftR - old_xleft)/diff_time
            if speed1 > speed_threshold:
                if xleftR-old_xleft > 120:
                    cv2.putText(original,'Last song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
                    xml = """<key state="press" sender="Gabbo">PREV_TRACK</key>"""
                    headers = {'Content-Type': 'application/xml'}
                    requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
                elif xleftR-old_xleft < 120:
                    cv2.putText(original,'Next song ',(20,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 1,cv2.LINE_AA)
                    xml = """<key state="press" sender="Gabbo">NEXT_TRACK</key>"""
                    headers = {'Content-Type': 'application/xml'}
                    requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            xleft = xleftR
            ytop = ytopR
        
    return original,frame, xleft, ytop


def video_capture():

    cap = cv2.VideoCapture(0)

    p = cv2.imread("./pause.jpg")
    s = cv2.imread("./play.jpg")
    r = cv2.imread("./uni_gesture.jpg")

    p = make_frame_smaller(p,1)
    s = make_frame_smaller(s,1)
    r = make_frame_smaller(r,1)

    templates = [p,s,r]

    time.sleep(5)
    _, first_frame = cap.read()
    first_frame = make_frame_smaller(first_frame,0.6)
    first_gray = gray_img(first_frame)
    
    time1 = 0
    xleft = 0
    ytop = 0
    while(True):
        ret, frame = cap.read()

        #make your frames smaller
        frame = make_frame_smaller(frame,0.6)
        original = frame.copy()
        
        #remove your back ground
        #frame = skin_detect(frame)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(first_gray, gray_frame)
        _, diff = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        
        #template matching for your object
        original, frame, xleft, ytop = template_matching(diff,templates,original,time1, xleft, ytop)

        cv2.imshow("Background", first_frame)
        cv2.imshow("difference", diff)
        cv2.imshow('frame',original)
        
        time1 = time.time()
        #press q to stop capturing frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

video_capture()

