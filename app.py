from flask import Flask, render_template, Response, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit
import cv2
import json

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html',async_mode=socketio.async_mode)

@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webhook', methods=['POST'])
def Webhook():
    temperature=""
    if request.method == 'POST':
        isFaceCapture = request.form.get('faceCapture')
        if(isFaceCapture):
            json_data = request.form['faceCapture']
            data_dict = json.loads(json_data)
            temperature = data_dict['faceCapture'][0]['faces'][0]['currTemperature']
            mask = data_dict['faceCapture'][0]['faces'][0]['mask']['value']
            print("MAsk : "+mask+" Temp : "+str(temperature))
            # print(data_dict)
        socketio.emit('datas-event',temperature)
        return '', 200
    else:
        abort(400)

def gen():
    RTSP_URL = 'rtsp://admin:abc12345@192.168.9.245/1/cif'
    cap = cv2.VideoCapture(RTSP_URL)
    while(True):
        ret, frame = cap.read()
        if not ret: #if vid finish repeat
            print("Can't receive frame (stream end?). Exiting ...")
            cap = cv2.VideoCapture(RTSP_URL)
            continue
        if ret:
            crop_frame = frame[62:620,241:998]
            frame = cv2.imencode('.jpg', crop_frame)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route("/mp3")
# def streamwav():
#     def generate():
#         with open("static/sounds/notification.mp3", "rb") as fwav:
#             data = fwav.read(1024)
#             while data:
#                 yield data
#                 data = fwav.read(1024)
#     return Response(generate(), mimetype="audio/x-wav")

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', port=4500,debug=True, use_reloader=True)
