from flask import Flask, render_template, Response, request, stream_with_context
from time import time

# For Motor Thread
from motor_thread import MotorThread
import os

# For CV Cam Streamming Thread
from cv_cam_thread import CvCamThread
import Queue

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('stream.html')

def gen_stream():
    frame_rcv_queue = Queue.Queue()
    cam_thread.reg_rcv_queue(frame_rcv_queue)
    while True:
        frame = frame_rcv_queue.get()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    # TODO: need to release frame_rcv_queue after streamming stopped.

@app.route("/video_feed")
def video_feed():
    return Response(stream_with_context(gen_stream()),
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
    return 'ajax_api called.'

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Start Motor Thread
        motor_thread = MotorThread()
        motor_thread.start()
        # Start CV Cam Thread
        cam_thread = CvCamThread()
        cam_thread.start()
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Stop Motor Thread
        motor_thread.stop_job()
        motor_thread.join()
        # Stop CV Cam Thread
        cam_thread.stop_job()
        cam_thread.join()
        print('Leaving Flask App.')
