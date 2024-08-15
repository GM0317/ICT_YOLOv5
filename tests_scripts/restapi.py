"""
Run a rest API exposing the custom YOLOv5 object detection model
"""
import argparse
import io
from PIL import Image

import torch
from flask import Flask, request

app = Flask(__name__)

DETECTION_URL = "/v1/object-detection/yolov5"

@app.route(DETECTION_URL, methods=["POST"])
def predict():
    if request.method == "POST":
        if request.files.get("image"):
            image_file = request.files["image"]
            image_bytes = image_file.read()

            img = Image.open(io.BytesIO(image_bytes))

            results = model(img, size=640)
            data = results.pandas().xyxy[0].to_json(orient="records")
            return data
    return "Invalid request", 400

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask api exposing yolov5 model")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    parser.add_argument("--model-path", default="C:/Users/ysh91/Downloads/exp24/exp24/weights/best.pt", type=str, help="path to custom model")
    args = parser.parse_args()

    # 커스텀 모델 로드
    model_path = args.model_path
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    model.eval()

    app.run(host="0.0.0.0", port=args.port)
