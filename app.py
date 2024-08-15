from flask import Flask, render_template, Response, jsonify
import cv2
import torch
import numpy as np
from PIL import Image
import serial
import time

app = Flask(__name__)

# 커스텀 모델 로드
model_path = 'C:/Users/ysh91/OneDrive/바탕 화면/yolov5fish/yolov5/best.pt'  # 사용자 정의 모델의 경로로 교체
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)

model.eval()
model.conf = 0.6  
model.iou = 0.45  

detected_status = '객체를 감지 못함'  # 기본 상태

def init_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return None

ser = init_serial('COM5', 9600)  # 아두이노가 연결된 포트로 교체
def gen():
    global detected_status
    cap = cv2.VideoCapture(0)  # 웹캠으로 변경
    if not cap.isOpened():
        print("Error: Could not open video stream")
        return

    # 비디오 스트림이 열려 있는 동안 프레임 읽기
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame")
            break
        else:
            try:
                # 프레임을 PIL 이미지로 변환
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                results = model(img, size=640)
                results.render()  # 예측 결과를 포함한 이미지 업데이트
                annotated_frame = np.squeeze(results.render())  # RGB 이미지
                annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)  # BGR 이미지

                # 여기서 음주자와 비음주자 식별
                labels = results.pandas().xyxy[0]['name'].values
                if len(labels) == 0:
                    new_status = '객체를 감지 못함'
                    if ser is not None:
                        ser.write(b'UNLOCK\n')  # 아두이노에 'UNLOCK' 메시지 전송
                elif 'drinker' in labels:
                    new_status = 'LOCK'
                    if ser is not None:
                        ser.write(b'LOCK\n')  # 아두이노에 'LOCK' 메시지 전송
                else:
                    new_status = 'UNLOCK'

                if detected_status != new_status:
                    detected_status = new_status  # 상태 업데이트

                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame = buffer.tobytes()
            except Exception as e:
                print(f"Error processing frame: {e}")
                continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', status=detected_status)

@app.route('/video')
def video():
    """비디오 스트리밍 경로. 이를 img 태그의 src 속성에 넣으십시오."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    global detected_status
    return jsonify(status=detected_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
