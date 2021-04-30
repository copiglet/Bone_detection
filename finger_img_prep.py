#!/usr/bin/env python
# coding: utf-8

# In[2]:


import cv2
import os
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns
import glob
import math
get_ipython().run_line_magic('matplotlib', 'inline')

#cv
import cv2
import math
from PIL import Image
import math
from scipy import ndimage
import argparse
import imutils


#시각화
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
get_ipython().run_line_magic('matplotlib', 'inline')

from matplotlib import font_manager, rc
rc('font',family="AppleGothic")
plt.rcParams["font.family"]="AppleGothic" #plt 한글꺠짐
plt.rcParams["font.family"]="Arial" #외국어꺠짐
plt.rcParams['axes.unicode_minus'] = False # 마이너스 부호 출력 설정
plt.rc('figure', figsize=(10,8))

sns.set(font="AppleGothic", 
        rc={"axes.unicode_minus":False},
        style='darkgrid') #sns 한글깨짐


# In[3]:


def direct_show(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    plt.figure(figsize = (10,8))
    #xticks/yticks - 눈금표
    plt.xticks([])
    plt.yticks([])
    #코랩에서 안돌아감 주의
    plt.imshow(img, cmap= 'gray')
    plt.show()


# In[4]:


def LOAD_IMG(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    return img


# In[2]:


def show(img):
    #사이즈
    plt.figure(figsize = (10,8))
    #xticks/yticks - 눈금표
    plt.xticks([])
    plt.yticks([])
    #코랩에서 안돌아감 주의
    plt.imshow(img, cmap= 'gray')
    plt.show()


# In[3]:


#이미지 수 확인하기
def count_img(path):
    data_path = os.path.join(path, '*g')
    files= glob.glob(data_path)
    img_list=[]
    for f1 in files:
        img = cv2.imread(f1)
        img_list.append(img)
    print('이미지수',len(img_list)) 


# In[4]:


#이미지 불러오기
def get_img(path):
    data_path = os.path.join(path, '*g')
    files= glob.glob(data_path)
    img_list=[]
    for f1 in files:
        img = cv2.imread(f1)
        img_list.append(img)
#     print('이미지수',len(img_list))
#     print('show(get_img(list_file[1])[0]) 식으로 이미지 불러와서 img로 저장')
    
    return img_list
    
# data_img = get_img(list_file[2])
# show(img_list[1])


# In[5]:


#masking, return 까먹지 말기 흑흑 
def get_mask(img):
    # #마스크 생성을 위해, 밝기 강조한 Lab으로 이미지 변환 01
    img = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    # #블러 02
    # #블러의 커널 사이즈가 홀수만 가능하므로 이미지 평균 값을 기준으로 홀수값 만들기
    blur_k = int((img.mean()*0.5)//2)*2+1 
    img = cv2.medianBlur(img, blur_k)
    # #threshold 적용을 위해 Lab에서 Grayscale로 이미지 변환 03
    img = cv2.cvtColor(img, cv2.COLOR_Lab2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # #이미지 평균값을 기준으로 이진화 04
    ret, img = cv2.threshold(img, img.mean()*1.1, 255, cv2.THRESH_BINARY)

    # # #가장 큰 값의 컨투어로 마스크 만들기 05
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_cnt = max(contours, key=cv2.contourArea)
    mask = np.zeros(img.shape, dtype=np.uint8)
    cv2.drawContours(mask, [max_cnt], -1, (255,255,255), -1)

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.dilate(mask,k)
    return mask

#img_cropping 
def get_cropped_mask(img, mask):
    """
    마스크를 기준으로 경계선을 찾아 위/왼/오른쪽을 자루는 함수로서
    img = original image
    mask = bit_img
    cropped_img = 원본 이미지에서 마크된 영역을 갖는 부분 반환
    """
    
    img_ = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img_.shape
    
    #마스크 기준으로 위/왼/오른쪽 경계선 찾기(숫자로 확인 가능)
    mask_list = mask.tolist()
    
    #테두리가 흰색인 경우를 고려해서, 테두리에서 5% 지점부터 경계점 찾기 시작
    #경계점은 중간 부분(30~70%)에서 검은색(0)을 벗어난 지점을 기준으로 함
    #위쪽
    for y in range(int(height*0.05), height): #마스크이미지에서, 일반 이미지의 5%이상의 지점에서 
    #가로는 30%-70%까지가 0보다 클때 (마스크의 max값이 - 그 범위에 1(흰색)이 있을때)
        if max(mask[y,int(width*0.3):int(width*0.7)]) >0:
        #총 mask 이미지에서, 일반이미지에서 5%더한 값을 뺌
            start_y = y-int(height*0.05)
            break
    
    #왼쪽 start point
    for x in range(int(width*0.05),width):
        if max(mask[x,int(height*0.3):int(height*0.7)]) >0:
            start_x = x-int(width*0.05)
            break

    # #오른쪽, stop, -1,-1(오른쪽에서 왼쪽으로)
    for x in range(int(width*0.95),-1,-1):
        if max(mask[int(height*0.3):int(height*0.7),x]) > 0:
            end_x = x+int(width*0.05)
            break

    #경계선 기준으로 이미지와 마스크 자름
    img_ = img_[start_y:,start_x:end_x]
    mask = mask[start_y:,start_x:end_x]

    img = cv2.bitwise_and(img_, mask)
    
    return img

def wrist_cut(img):
    height = img.shape[0]
    width = img.shape[1]

    #이미지의 아래에서부터 시작해서 화소 평균이 커지는(밝아지는) 경계선 찾기
    start = int(height*0.95)  #아래 테두리가 밝은 경우를 고려해서 height*0.95부터 시작함
    index = 0
    k = 10 #10개 행씩 평균 구함
    while True:
        pixel_lower = img[start-k*(index+1):start-k*index,:].mean()
        pixel_upper = img[start-k*(index+2):start-k*(index+1),:].mean()
        if pixel_upper - pixel_lower > 0:
            end_y = start-k*(index+1)
            break
        index += 1

    img = img[:end_y]
    return img

def mask_for_center(img):
    blur_k = int((img.mean()*0.5)//2)*2+1 
    img = cv2.medianBlur(img, blur_k)

    # #이미지 평균값을 기준으로 이진화 04
    ret, img = cv2.threshold(img, img.mean()*1.1, 255, cv2.THRESH_BINARY)

    # # #가장 큰 값의 컨투어로 마스크 만들기 05
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_cnt = max(contours, key=cv2.contourArea)
    mask = np.zeros(img.shape, dtype=np.uint8)
    cv2.drawContours(mask, [max_cnt], -1, (255,255,255), -1)

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.dilate(mask,k)
    return mask



#img_preprocessing
def blake_back(img):
    mask =get_mask(img)
    black_back = get_cropped_mask(img, mask)
    black_back = wrist_cut(black_back)
    center_mask = mask_for_center(black_back)
    return black_back, center_mask


# In[6]:


def get_center(center_mask):
#     mask = mask_for_center(img)
    res, thresh = cv2.threshold(center_mask, center_mask.mean(), 255, cv2.THRESH_BINARY)

    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    
    return cX, cY

def get_far_list(img):
    #손가락포인트
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_cnt = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(max_cnt, returnPoints = False)
    defects = cv2.convexityDefects(max_cnt, hull)
    
    far_list = []
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(max_cnt[s][0])
        end = tuple(max_cnt[e][0])
        far = tuple(max_cnt[f][0])
        far_list.append(far)
        
    return far_list

def get_pinky_point(far_list):
    far_list.sort(key = lambda x:x[0])
    pX, pY = far_list[0]
    return pX, pY

def get_thumbs_point(far_list):
    far_list.sort(key = lambda x:x[0])
    thX, thY = far_list[-1]
    return thX, thY

def get_middle_point(far_list):
    far_list.sort(key = lambda x:x[0])
    tX, tY = far_list[-1]
    return tX, tY

#point
def get_pinky_finger_point(center_mask, black_back):
    cX, cY = get_center(center_mask)
    far_list = get_far_list(black_back)
    pX, pY = get_pinky_point(far_list)
    return cX, cY, pX, pY

def get_thumbs_finger_point(center_mask, black_back):
    cX, cY = get_center(center_mask)
    far_list = get_far_list(black_back)
    thX, thY = get_thumbs_point(far_list)
    return cX, cY, thX, thY

def get_middle_finger_point(center_mask, black_back):
    cX, cY = get_center(center_mask)
    far_list = get_far_list(black_back)
    tX, tY = get_middle_point(far_list)
    return cX, cY, tX, tY


# In[7]:


def rotation_cut(img):
    img = ndimage.rotate(img, 70)
    ret, th = cv2.threshold(img, img.mean(), 255, cv2.THRESH_BINARY)
    th_l = th.tolist()
    cut_index = 0
    if th_l[0][0] == 0 or th_l[0][-1] == 0:
        for i in reversed(range(len(th_l))):
            if th_l[i].count(255) > 0:
                cut_index = i

    img = img[cut_index:]
    return img

def center_img(img):
    imgY, imgX = img.shape[:2]
    imgY = int((imgY)/2)
    imgX = int(imgX/2)
    
    return imgY, imgX


# In[8]:


def pinky_rotation(img):
    angle = math.degrees(math.atan2(cY-thY, cX-thX))
    img = ndimage.rotate(img, angle-100)#시계방향
    return img

def rotation_cut(img):
    ret, th = cv2.threshold(img, img.mean(), 255, cv2.THRESH_BINARY)
    th_l = th.tolist()
    cut_index = 0
    if th_l[0][0] == 0 or th_l[0][-1] == 0:
        for i in reversed(range(len(th_l))):
            if th_l[i].count(255) > 0:
                cut_index = i

    img = img[cut_index:]
    return img

def center_img(img):
    imgY, imgX = img.shape[:2]
    imgY = int((imgY)/2)
    imgX = int(imgX/2)
    
    return imgY, imgX


#rotation / get_imgYX
def get_imgYX(img):
    rotated_img = pinky_rotation(img)
    show(rotated_img)
    img = rotation_cut(rotated_img)
    show(img)
    imgY, imgX = center_img(img)
    return img, imgY, imgX


# In[1]:


def get_img_croped(img):
    ret, thresh = cv2.threshold(img, img.mean(), 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_xy = np.array(contours)

    # x의 min과 max 찾기
    x_min, x_max = 0,0
    value = list()
    for i in range(len(contours_xy)):
        for j in range(len(contours_xy[i])):
            value.append(contours_xy[i][j][0][0]) #네번째 괄호가 0일때 x의 값
            x_min = min(value)
            x_max = max(value)
#     print(x_min)
#     print(x_max)

    # y의 min과 max 찾기
    y_min, y_max = 0,0
    value = list()
    for i in range(len(contours_xy)):
        for j in range(len(contours_xy[i])):
            value.append(contours_xy[i][j][0][1]) #네번째 괄호가 0일때 x의 값
            y_min = min(value)
            y_max = max(value)
#     print(y_min)
#     print(y_max)

    # image trim 하기
    x = x_min
    y = y_min
    w = x_max-x_min
    h = y_max-y_min

    img_trim = img[y:y+h, x:x+w]
    
    return img_trim 


# In[5]:


#for wrist cropping
def rotate_and_cut_base(img, draw=False):
    """
    마스크 기준으로 아래쪽 자르기 및 회전하는 함수
    
    Parameters:
    img : 마스크된 이미지 객체
    draw : 기본값 False, True일 경우 중신선을 그려줌
    
    Returns:
    rotate : 회전 및 아래쪽이 잘린 이미지 객체
    """
    ###아래 테두리가 흰색 또는 검은색인 경우를 고려해서 아래부분 자르기
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    th_l = th.tolist()

    cut_index = 0
    # 맨 밑 처음이나 끝에 흰색이 나오면 검은색이 나오는 부분까지 자르기
    if th_l[len(th_l)-1][-1] == 255 or th_l[len(th_l)-1][0] == 255:
        for i in reversed(range(len(th_l))):
            if th_l[i][0] == 0 and th_l[i][-1] == 0:
                cut_index = i
                break

    # 맨 밑 처음이 검정색이면 흰색이 나오는 부분까지 자르기
    if th_l[len(th_l)-1][0] == 0 or th_l[len(th_l)-1][-1] == 0:
        for i in reversed(range(len(th_l))):
            if th_l[i].count(255) > 0:
                cut_index = i
                break

    if cut_index == 0:
        cut_index = len(th_l)

    img = img[:(cut_index-1)]

    ###회전하기
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    th_l = th.tolist()

    # 밑에서부터 처음으로 검은 색이 나오는 부분이 lower
    for i in reversed(range(len(th_l))):
        if th_l[i][0] == 0:
            lower = i
            break

    # 만약 맨 밑이 lower면 이미지의 90퍼센트 부분을 lower로 정의
    if lower == h - 1:
        lower = int(len(th_l)*0.9)

    # upper는 lower에서 5퍼센트만큼 올라간 부분
    slice5 = int(len(th)*0.05)
    upper = lower - slice5

    # x, y좌표들은 이미지의 85퍼센트(upper)와 90퍼센트(lower) 부분의 손목 가운데 지점들
    x,y = [],[]
    for i in range(slice5):
        cnt = th_l[i + upper].count(255)
        index = th_l[i + upper].index(255)
        x.append([i+upper])
        y.append([int((index*2 + cnt - 1)/2)])

    # x,y좌표로 단순선형회귀 그리기
    model = LinearRegression()
    model.fit(X=x,y=y)

    # 중심선을 그려줌
    if draw:
        draw = cv2.line(img,(int(model.predict([[0]])),0),(int(model.predict([[h]])),h),(255,0,255),3)

    # 회전
    angle = math.atan2(h - 0, int(model.predict([[h]])) - int(model.predict([[0]])))*180/math.pi
    M = cv2.getRotationMatrix2D((w/2,h/2),angle-90,1)
    rotate = cv2.warpAffine(img, M, (w,h))

    # 회전한 부분을 자르기
    for i in range(len(th[-1])):
        if th[-1][i] == 255:
            start_x = i
            break

    for i in range(len(th[-1])):
        if th[-1][i] == 255:
            end_x = i

    s_point = h - int((int(model.predict([[h]])-start_x)) * math.tan(math.pi*((90-angle)/180)))
    e_point = h - int((end_x - int(model.predict([[h]]))) * math.tan(math.pi*((angle-90)/180)))
    point = min(s_point, e_point)

    return rotate[:point]

def find_far_right_lower(mask):
    """
    중심점보다 오른쪽 아래에 있는 점들을 구하는 함수

    Parameters:
    mask : ndarray, rotate_and_cut_base() 함수의 결과 이미지
    
    Returns:
    far_right_lower : 중심점 보다 오른쪽 아래에 있는 점들
    """
    
    height, width = mask.shape[:2]
    
    #마스크 기준으로 컨투어 및 중심점 구하기
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_cnt = max(contours, key=cv2.contourArea)
    (x,y), radius = cv2.minEnclosingCircle(max_cnt)
    center = (int(x),int(y)) #중심점
    hull = cv2.convexHull(max_cnt, returnPoints = False)
    defects = cv2.convexityDefects(max_cnt, hull)

    far_right_lower = []
    for index in range(defects.shape[0]):
        s,e,f,d = defects[index,0]
        far = tuple(max_cnt[f][0])

        #far 좌표가 중심점보다 오른쪽 아래에 있고, 이미지 테두리보다 안쪽에 있는 점
        if (far[0] > center[0]) and (far[1] > center[1]) and (far[0] <= width*0.95) and (far[1] <= height*0.95):
            far_right_lower.append(far)
    
    return far_right_lower

#중심선을 그리되, 그림에 넣진 않음
def get_roi(img, draw=False):
    """
    중심점보다 오른쪽 아래에 있는 점들을 구하는 함수

    Parameters:
    img : ndarray, rotate_and_cut_base() 함수의 결과 이미지
    draw : 기본값 Falsw, True일 경우
    
    Returns:
    roi : 손목 부분의 ROI 이미지 객체
    """
    
    img_ = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   
    height, width = img_.shape    
    
    #이미지의 아래에서부터 시작해서 화소 평균이 커지는(밝아지는) 경계선 찾기
    start = int(height*0.95)  #아래 테두리가 밝은 경우를 고려해서 height*0.95부터 시작함
    index = 0
    k = 10 #10개 행씩 평균 구함
    while True:
        pixel_lower = img_[start-k*(index+1):start-k*index,:].mean()
        pixel_upper = img_[start-k*(index+2):start-k*(index+1),:].mean()
        if pixel_upper - pixel_lower > 0:
            end_y = start-k*(index+1)
            break
        index += 1

    img = img[:end_y]

    #엄지-손목 경계점 기준으로 ROI
    img_ = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   

    ret, mask = cv2.threshold(img_, 10, 255, cv2.THRESH_BINARY)

    far_right_lower = find_far_right_lower(mask)

    #오른쪽 아래에 있는 점이 없는 경우, resize해서 함수 재실행
    if len(far_right_lower) == 0:
        resize_height = 800
        resize_width = 600
        img = cv2.resize(img, (resize_height, resize_width), interpolation=cv2.INTER_AREA)
        mask = cv2.resize(mask, (resize_height, resize_width), interpolation=cv2.INTER_AREA)
        far_right_lower = find_far_right_lower(mask)

    #추가한 far 좌표 중 가장 아래쪽에 있는 좌표(엄지 손가락과 손목 경계점) 기준으로, ROI 영역 구함
    max_far = max(far_right_lower, key = lambda x:x[1]) 
    end_x = max_far[0]
    end_y = int(max_far[1]*1.1) #1.1은 임의의 숫자. ROI를 아래쪽으로 확대하고 싶으면 숫자 늘리기.
    start_y = int(max_far[1]*0.78) #0.78은 임의의 숫자. ROI를 위쪽으로 확대하고 싶으면 숫자 줄이기.
    start_x = np.argmax(mask[max_far[1],:])

    if draw:
        cv2.rectangle(img, (start_x, start_y), (end_x, end_y), (0,255,0), 3)
        return img

    roi = img[start_y:end_y,start_x:end_x]
    return roi    

#contrast
def contrast(img, low, high):
    h, w = img.shape
    img_ = np.zeros(img.shape, dtype=np.uint8)
    
    for y in range(h):
        for x in range(w):
            temp = int( (255/(high-low)) * (img[y][x]-low) )
            if temp > 255:
                img_[y][x] = 255
            elif temp < 0:
                img_[y][x] = 0
            else:
                img_[y][x] = temp
    
    return img_

#사이즈 조절하기 싫을 때 size=False
def get_roi_final(img, size=(200, 150)) :
    """
    ROI를 강조

    Parameters:
    roi : ndarray, get_roi() 함수의 결과 이미지
    size : 기본값 (200, 150), 지정한 크기로 표준화함, None 또는 False일 경우 원본 roi 크기로 반환함
    
    Returns:
    img : 손목 부분의 ROI 이미지 객체
    """
    img = roi.copy()

    ###이진화
    #마스크 생성을 위해, 밝기 강조한 Lab으로 이미지 변환
    img = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)

    #모폴로지
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
    img = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, k)

    #블러
    img = cv2.GaussianBlur(img, (15, 15), 0)

    #threshold 적용을 위해 Lab에서 Grayscale로 이미지 변환
    img = cv2.cvtColor(img, cv2.COLOR_Lab2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #이진화
    ret, mask = cv2.threshold(img, np.mean(img), 255, cv2.THRESH_BINARY)

    #컨투어
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(mask, contours, -1, (255,255,255), -1)


    ###강조
    img = roi.copy()

    #모폴로지
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
    img = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, k)

    #contrast
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if img.mean() <= 15:
        low = img.mean()*1.5
        high = img.mean()*1.6
    elif img.mean() <= 20:
        low = img.mean()*1.5
        high = img.mean()*1.8
    else:
        low = img.mean()*1.5
        high = img.mean()*2

    img = contrast(img, low, high)

    #컨투어
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (255,255,255), -1)

    #마스크랑 비트 연산
    img = cv2.bitwise_and(img, mask)
    
    if size:
        #크기 표준화
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        return img
    else :
        return img


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[10]:


#get skin removed
def binarization3(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_hist = cv2.equalizeHist(img_gray)
    ret, thr = cv2.threshold(img_hist,img_gray.mean(),255,cv2.THRESH_TOZERO)
    img_hist = cv2.equalizeHist(thr)
    ret1, thr1 = cv2.threshold(img_hist,thr.mean(),255,cv2.THRESH_TOZERO)
    clahe = cv2.createCLAHE(clipLimit=img_gray.mean(), tileGridSize=(1,1))
    clahe_img = clahe.apply(thr1)
    final_img = cv2.threshold(clahe_img, clahe_img.mean(),255, cv2.THRESH_TOZERO)[1]
    return final_img


# In[ ]:




