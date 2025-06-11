# 차량 감지 알림 시스템 (Vehicle Alert System)

OBS 가상카메라 영상을 실시간 분석하여, 지정한 영역(ROI) 내 차량을 감지하면 경비원에게 알림을 주는 Python 기반 감시 시스템입니다.

---

## 📦 주요 기능

- 📷 OBS 가상카메라 입력 실시간 분석
- 🎯 ROI(관심영역) 지정 인터페이스 (PySimpleGUI 사용)
- 🚗 YOLOv5n 기반 차량 탐지
- 🧠 모션 감지 + 추론 빈도 최적화
- 📂 감지 기록 로그 자동 저장
- 🔔 차량 감지 시 알림 발생 (사운드/출력 등 확장 가능)

---

## 🖥️ 설치 방법

```bash
# 가상환경 권장
python -m venv venv
venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

---

## 🛠️ 사용 방법

1. **OBS Studio에서 '가상카메라 시작'**  
   (CCTV 프로그램을 디스플레이 캡처로 설정)

2. **ROI 설정 실행**  
   ```bash
   python src/ROI_Four_Dots.py
   ```
   - 화면 위에 4개의 점을 찍어서 감지 영역 지정
   - Ctrl+Z: 점 삭제 / Ctrl+S 또는 ESC: 저장

3. **프로그램 실행**  
   ```bash
   python src/main.py
   ```

4. **차량이 감지되면** 콘솔에 알림이 출력되고, 로그가 기록됩니다.

---

## 🧠 모델 파일 다운로드

`src/models/yolov5n.pt` 파일은 직접 다운로드해야 합니다.  
아래 링크에서 YOLOv5n 모델을 받아서 `src/models/` 폴더에 넣어주세요:

- [YOLOv5 모델 다운로드 (Ultralytics)](https://github.com/ultralytics/yolov5)

---

## 📁 폴더 구조

```
Car_Detection/
├── src/
│   ├── models/           ← YOLO 모델 파일 위치
│   ├── main.py           ← 실행 진입점
│   ├── ROI_Four_Dots.py  ← ROI 점 찍기
│   ├── Big_Filtering.py  ← 차량 감지 로직
│   └── Select_Profile.py ← ROI 관리 인터페이스
├── logs/                 ← 차량 감지 기록
├── .gitignore
├── README.md
```

---

## 📄 라이선스

이 프로젝트는 **GPLv3 라이선스**를 따릅니다.  
전체 소스코드는 자유롭게 사용할 수 있으며, 상업적으로 사용하려면 소스코드를 함께 공개해야 합니다.

> YOLOv5, PyQt5, OBS 가상카메라 등 GPL 기반 구성요소 포함