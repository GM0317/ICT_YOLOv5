import torch
from PIL import Image

model_path = 'C:/Users/ysh91/Downloads/exp24/exp24/weights/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
model.eval()

img = Image.open('C:/Users/ysh91/Downloads/Drunk.v5-zibs.yolov5pytorch/train/images/Drunkface4B1_jpeg.rf.dbe7ece33d53bbdee56bc561a305a2db.jpg')  # 테스트할 이미지를 여기에 대입
results = model(img)
results.show()  # 이미지에 바운딩 박스를 포함한 결과를 보여줌
