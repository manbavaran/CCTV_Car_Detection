
# CCTV 차량 감지 알림 시스템

경비실/관제실 환경에서 CCTV 화면을 실시간으로 분석하여  
차량 진입 시 소리로 경보를 주는 초경량 감지 프로그램입니다.

---

## 주요 기능

- **실시간 CCTV 차량 감지**  
  - 가상카메라/OBS 화면 입력 지원
  - 초경량 ONNX 딥러닝 모델 사용 (yolov5n)

- **ROI(관심영역) 설정**
  - 마우스로 네 점을 클릭하여 감지 구역 지정
  - 감지 화면, ROI 설정 화면 모두 “모니터 최대 해상도”로 표시

- **알림음(경보) 기능**
  - 차량이 ROI 내에 감지되면 설정된 경보음 반복 재생

- **최소화된 경량 구조**
  - 불필요한 부가 기능 제거, 설치/사용/유지보수 간편

---

## 설치 및 실행

1. **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

2. **ROI 영역 설정**
    - 프로그램 실행 후 [ROI 설정] 버튼 클릭
    - 화면에 네 점 클릭 → ESC로 저장/종료

3. **감지 시작**
    - [감지 시작] 버튼 클릭
    - 차량 진입 시 경보음이 울림

---

## 폴더 구조

```
src/
  main.py            # 실행 메인 파일
  VehicleDetector.py # 감지 및 알림
  ROI_Four_Dots.py   # ROI 설정 창
  roi_io.py          # ROI 좌표 저장/불러오기
  logger.py          # 간단 로그
  models/
    yolov5n.onnx     # 차량 감지용 ONNX 모델
resources/
  sounds/Car_Alarm.mp3 # 알림음(mp3)
```

---

## 환경/권장사양

- **Windows 10 64bit**  
- **Python 3.10+**
- **CPU만으로 동작 (GT 730, 내장그래픽 가능)**
- **OBS 가상카메라 등 지원**

---

## 참고

- ONNX 모델: [YOLOv5n](https://github.com/ultralytics/yolov5)  
- 차량 클래스: car, motorcycle, bus, truck(COCO 기준)

---

## 문의 및 사용법

- 궁금한 점이나 개선 요청은 [Issues](https://github.com/manbavaran/CCTV_Car_Detection/issues) 탭 활용
- 실 운영 환경에 맞게 ROI와 경보음을 조절해 주세요

---
