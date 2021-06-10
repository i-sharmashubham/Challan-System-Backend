import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import requests
from Models import Owner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#ChallanUrl = 'http://127.0.0.1:8000/createchallan'
ChallanUrl = 'https://shubham-anpr.herokuapp.com/createchallan'
patt = re.compile(r'[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}')
engine = create_engine('mysql://sql6417125:rssY2fGVIJ@sql6.freesqldatabase.com:3306/sql6417125')


def CaptureVideo(path):
    pass

def CaptureImage(path):
    img = cv2.imread(path)
    return img

def PreProcessing(frame):
    img = cv2.GaussianBlur(frame, (5,5), 0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    img = cv2.Sobel(img,cv2.CV_8U,1,0,ksize=3)	
    _,img = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    return img

def PlateLocalization(frame,image):
    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
    morph_img_threshold = frame.copy()
    cv2.morphologyEx(src=frame, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)
    num_contours, hierarchy= cv2.findContours(morph_img_threshold,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(frame, num_contours, -1, (0,255,0), 1)

    for i,cnt in enumerate(num_contours):
        min_rect = cv2.minAreaRect(cnt)
        if ratio_and_rotation(min_rect):
            x,y,w,h = cv2.boundingRect(cnt)
            plate_img = image[y:y+h,x:x+w]
            if(isMaxWhite(plate_img)):
                clean_plate, rect = clean2_plate(plate_img)
                if rect:
                    return clean_plate

def CharacterRecognition(localizedPlate): 
    text = pytesseract.image_to_string(localizedPlate, lang='eng')
    return number_validation(text)

def createChallan(image,data):
    imencoded = cv2.imencode(".jpg", image)[1]
    file = {'file': ('image.jpg', imencoded.tobytes(), 'image/jpeg', {'Expires': '0'})}
    x = requests.post(ChallanUrl, data = data, files=file)
    return x.ok

def get_owner_data(regno):
    Session = sessionmaker(bind = engine)
    session = Session()
    result = session.query(Owner).filter(Owner.reg_no == regno).first()
    session.close()
    return result

def clean2_plate(plate):
    gray_img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY)
    if cv2.waitKey(0) & 0xff == ord('q'):
        pass
    num_contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if num_contours:
        contour_area = [cv2.contourArea(c) for c in num_contours]
        max_cntr_index = np.argmax(contour_area)

        max_cnt = num_contours[max_cntr_index]
        max_cntArea = contour_area[max_cntr_index]
        x,y,w,h = cv2.boundingRect(max_cnt)

        if not ratioCheck(max_cntArea,w,h):
            return plate,None

        final_img = thresh[y:y+h, x:x+w]
        return final_img,[x,y,w,h]

    else:
        return plate,None

def ratioCheck(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio
    if (area < 1063.62 or area > 73862.5) or (ratio < 3 or ratio > 6):
        return False
    return True
    
def isMaxWhite(plate):
    avg = np.mean(plate)
    if(avg>=115):
        return True
    else:
        return False
    
def ratio_and_rotation(rect):
    (x, y), (width, height), rect_angle = rect

    if(width>height):
        angle = -rect_angle
    else:
        angle = 90 + rect_angle

    if angle>15:
        return False

    if height == 0 or width == 0:
        return False

    area = height*width
    if not ratioCheck(area,width,height):
        return False
    else:
        return True

def apply_filter(text):
    if len(text) == 10:
        state = ''
        dist = ''
        alpha = ''
        num = ''
        for c in text[0:2]:
            if c=='0':
                state += 'O'
            else:
                state += c
        for c in text[2:4]:
            if c=='O':
                dist += '0'
            else:
                dist += c
        for c in text[4:6]:
            if c=='0':
                alpha += 'O'
            else:
                alpha += c
        for c in text[6:10]:
            if c=='O':
                num += '0'
            else:
                num += c
        return state+dist+alpha+num
    if len(text) == 9:
        state = ''
        dist = ''
        alpha = ''
        num = ''
        for c in text[0:2]:
            if c=='0':
                state += 'O'
            else:
                state += c
        for c in text[2:4]:
            if c=='O':
                dist += '0'
            else:
                dist += c
        for c in text[4:5]:
            if c=='0':
                alpha += 'O'
            else:
                alpha += c
        for c in text[5:9]:
            if c=='O':
                num += '0'
            else:
                num += c
        return state+dist+alpha+num
    return text

def number_validation(text):
    text = str("".join(re.split("[^a-zA-Z0-9]*", text)))
    text.upper()
    if len(text) <= 10:
        text = apply_filter(text)
    res = patt.search(text)
    if res is None:
        filtered_text = apply_filter(text)
        res = patt.search(filtered_text)
        if res is None:
            return False,text
    return True,res.group()