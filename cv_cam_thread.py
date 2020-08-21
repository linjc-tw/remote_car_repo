# For CV Cam Thread
import threading
import Queue
import cv2

class CvCamThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'CV Cam Thread'
        self.do_job = True
        self.queue = Queue.Queue()
        self.lock = threading.Lock()
        # Init CV Cam
        self.video = cv2.VideoCapture(0)
        self.reg_queues = []

    def __del__(self):
        self.video.release()

    def run(self):
        print('Starting', self.name)
        while self.do_job:
            # Check Message Queue
            success, image = self.video.read()
            ret, jpeg = cv2.imencode('.jpg', image)
            # send jpeg to other each receiving queues.
            for queue in self.reg_queues:
                queue.put(jpeg.tostring())

    def stop_job(self):
        print('Exit %s' % (self.name))
        self.do_job = False

    def reg_rcv_queue(self, queue):
        self.reg_queues.append(queue)
