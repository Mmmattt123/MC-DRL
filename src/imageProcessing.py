import numpy as np
from PIL import ImageGrab
import cv2
from utilities import fps_logger

BGR_LOW = np.array([0,0,0])

BLUE_LOW = np.array([60,0,0])
GREEN_LOW = np.array([0,50,0])
RED_LOW = np.array([0,0,60])

BLUE_HIGH = np.array([225,80,80])
GREEN_HIGH = np.array([80,225,80])
RED_HIGH = np.array([80,80,225])

ROI_SHAPE = np.array([[300,150],[660,150],[660, 410],[300,410]])

class ImageProcessor:

    def start(self):
        while(True):
            self.screenRecord()
            if cv2.waitKey(25) & 0xFF == ord('p'):
                cv2.destroyAllWindows()
                break
 

    @fps_logger
    def screenRecord(self): 
        screen = np.array(ImageGrab.grab(bbox=(0,60,960,560)))
        gray_img, mixed_img, r_img = self.processImg(screen)

        

        cv2.imshow('window1', gray_img)
        cv2.imshow('window original', cv2.cvtColor(mixed_img, cv2.COLOR_BGR2RGB))
        #cv2.imshow('window2', b_img)
        #cv2.imshow('window3', g_img)
        cv2.imshow('window4', r_img)




    def processImg(self, o_img):
        #grey image
        #gray_img = cv2.GaussianBlur(o_img, (5,5), 0)
        #gray_img = cv2.bilateralFilter(gray_img,9,75,75)
        gray_img = cv2.cvtColor(o_img, cv2.COLOR_BGR2GRAY)
        mixed_img = o_img
        gray_img = cv2.Canny(gray_img, threshold1=50, threshold2=200)
        gray_img = self.roi(gray_img,ROI_SHAPE)


        lines = cv2.HoughLinesP(gray_img, 1, np.pi/180, 100, np.array([]), 10, 5)
        self.drawLines(gray_img,lines)
        self.drawLines(mixed_img, lines)
        #o_img = cv2.cvtColor(o_img, cv2.COLOR_BGR2RGB)
        #blue image
        #b_img = cv2.inRange(o_img, BLUE_LOW, BLUE_HIGH)
        #b_img = cv2.Canny(b_img, threshold1=90, threshold2=300 )

        #g_img = cv2.inRange(o_img, GREEN_LOW, GREEN_HIGH)
        #g_img = cv2.Canny(g_img, threshold1=90, threshold2=300 )

        r_img = cv2.inRange(o_img, RED_LOW, RED_HIGH)
        #r_img = cv2.Canny(r_img, threshold1=90, threshold2=300 )

        return gray_img, mixed_img, r_img
    

    def roi(self,img, vertices): 
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, [vertices],255)
        masked = cv2.bitwise_and(img, mask)
        return masked


    def drawLines(self, img, lines):
        try:
            for line in lines:
                coords = line[0]
                cv2.line(img, (coords[0],coords[1]), (coords[2], coords[3]),[255,0,0], 3 )
        except:
            pass