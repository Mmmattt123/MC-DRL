import time

def fps_logger(function):
    def wrapper(*args,**kwargs):
       b_time = time.time()
       function(*args,**kwargs) 
       c_fps = 1 / (time.time() - b_time)
       print("CURRENT FPS: {}".format(c_fps))
    return wrapper


