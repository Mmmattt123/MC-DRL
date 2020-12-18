import numpy as np
from PIL import ImageGrab
import cv2
import time
from utilities import logger, csv_logger, FileManager
from memory_profiler import profile

GPU = 'gpu'
CPU = 'cpu'

BGR_LOW = np.array([0,0,0])

BLUE_LOW = np.array([60,0,0])
GREEN_LOW = np.array([0,50,0])
RED_LOW = np.array([0,0,60])

BLUE_HIGH = np.array([225,80,80])
GREEN_HIGH = np.array([80,225,80])
RED_HIGH = np.array([80,80,225])

ROI_SHAPE = np.array([[300,150],[660,150],[660, 410],[300,410]])
fp = open('./memory_profile.log','w+')
CSV_HEADERS =  "processor, function, execution_time, fps\n"

class ImageProcessor:

    def __init__(self):
        self.stats = {
            GPU: {},
            CPU: {},
        }

    def start(self):
        """
        gray_img = cv2.Canny(gray_img, threshold1=50, threshold2=200)

        gray_img = cv2.GaussianBlur(, (5,5), 0)

        gray_img = cv2.bilateralFilter(,9,75,75)
        """

        with FileManager("./stats.csv", "w") as f:
            f.write(CSV_HEADERS)

        self.test_function(cv2.GaussianBlur, CPU, 50, ((5,5), 0)) 
        self.test_function(cv2.GaussianBlur, GPU, 100, ((5,5), 0))

        self.test_function(cv2.bilateralFilter, CPU, 50, (9,75,75))
        self.test_function(cv2.bilateralFilter, GPU, 100,(9,75,75) )

        #self.test_function(cv2.Canny, CPU , ( threshold1=50, threshold2=200) )
        #self.test_function(cv2.Canny, GPU , ( threshold1=50, threshold2=200) )

        feasible = self.fease()
        print(feasible)
        while(True):
            self.test_function(cv2.GaussianBlur, feasible, 100, ((5,5), 0))   
            if cv2.waitKey(25) & 0xFF == ord('p'):
                cv2.destroyAllWindows()
                break
    
    def fease(self):
        cpu = self.processor_average(self.stats[CPU])
        gpu = self.processor_average(self.stats[GPU])

        if np.average(cpu) > np.average(gpu): 
            return CPU
        else: 
            return GPU
    
    def processor_average(self, functions): 
        avg = np.array([])
        for function in functions: 
            avg = np.append(avg, np.average(functions[function]))
        return avg

    def test_function(self, function, processor, limit, f_args):
        stat_array = np.array([])
        while  stat_array.size < limit:
            image = self.prepare_image( processor)
            time = self.screenRecord(image, function, f_args)
            self.write_log(function, processor, time)
            stat_array = np.append(stat_array, 1/time)
            if cv2.waitKey(25) & 0xFF == ord('p'):
                cv2.destroyAllWindows()
                break
        self.stats[processor][function.__name__] = stat_array 


    @profile(stream=fp)
    def prepare_image(self, processor): 
        screen_matrix = ImageGrab.grab(bbox=(0,60,960,560))
        screen = np.array(screen_matrix)

        if processor == GPU: 
            screen = cv2.UMat(screen)
        return screen

    def screenRecord(self, image, function, f_args): 
        
        b_time = time.time()
        gray_img, mixed_img, r_img = self.process_img_with_function(image,function, f_args)
        a_time = time.time()
        
        cv2.imshow('window1', gray_img)
        cv2.imshow('window original', cv2.cvtColor(mixed_img, cv2.COLOR_BGR2RGB))
        cv2.imshow('window4', r_img)
        
        return a_time - b_time 

    def write_log(self,function, processor, time): 
        log = processor + ',' + function.__name__ + ', ' + str(time) +  ", " + str(1 /time) +'\n'
        with FileManager("./stats.csv", 'a') as f:
            f.write(log)

    @profile(stream=fp)
    def process_img_with_function(self, o_img, function, f_args):
        mixed_img = o_img

        r_img = cv2.inRange(o_img, RED_LOW, RED_HIGH)
        gray_img = cv2.cvtColor(o_img, cv2.COLOR_BGR2GRAY)

        r_img = function(r_img, *f_args)
        gray_img = function(gray_img,  *f_args)

        lines = cv2.HoughLinesP(gray_img, 1, np.pi/180, 200, np.array([]), 10, 5)
        lines2 = cv2.HoughLinesP(r_img, 1, np.pi/180, 100, np.array([]), 10, 5)

        self.drawLines(gray_img, lines2)
        self.drawLines(r_img, lines2)
        #self.drawLines(mixed_img, lines)
        #self.drawLines(mixed_img,lines2)

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