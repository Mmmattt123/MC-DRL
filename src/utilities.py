import time
import numpy as np

class FileManager(): 
    def __init__(self, filename, mode): 
        self.filename = filename 
        self.mode = mode 
        self.file = None
          
    def __enter__(self): 
        self.file = open(self.filename, self.mode) 
        return self.file
      
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.file.close() 

def logger(function):
    def wrapper(*args, **kwargs):
       b_time = time.time()
       function(*args, **kwargs)
       c_fps = 1 / (time.time() - b_time)
       print("CURRENT FPS: {}".format(c_fps))
    return wrapper

def csv_logger(function):
    def wrapper(*args, **kwargs):
        with FileManager('./stats.csv', 'w+') as csv_file: 
            csv_file.write(function(*args,**kwargs))
    return wrapper

