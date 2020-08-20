from flask import Flask, render_template, Response, request, stream_with_context
from time import time

# For Motor Thread
from motor_thread import MotorThread
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('stream.html')

import cv2
class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(stream_with_context(gen(Camera())),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/ajax_api")
def ajax_api():
    cmd = request.args.get('cmd')
    param_1 = request.args.get('param_1')
    param_2 = request.args.get('param_2')
    print('cmd =', cmd)
    print('param_1=', param_1)
    print('param_2=', param_2)

    motor_thread.set_speed(int(param_1), int(param_2))

    '''
    if cmd == 'move':
    if param_1 == 'turn_left':
      turn_left()
    elif param_1 == 'turn_right':
      turn_right()
    elif param_1 == 'forward':
      forward()
    elif param_1 == 'backward':
      backward()
    elif cmd == 'stop':
    stop()
    else:
    print('unknown cmd:', cmd)
    '''

    return 'ajax_api called.'


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        #initMotors() # need to put into MotorThread.
        motor_thread = MotorThread()
        motor_thread.start() # Start Motor Thread
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        motor_thread.stop_job() # Stop Motor Thread
        motor_thread.join()
        print('Leaving Flask App.')
