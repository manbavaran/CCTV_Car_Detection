# 차량 감지 알림 시스템 (Vehicle Alert System)

OBS 가상카메라 화면을 분석하여, 지정한 ROI(관심 영역) 내에서 차량이 감지되면 사용자에게 사운드 알림과 로그 기록을 제공하는 실시간 감시 시스템입니다.

---

## ✅ 주요 기능

- 📷 **OBS 가상카메라 실시간 입력 감지**
- 🖼️ **PyQt5 기반 ROI 설정 및 GUI 제어**
- 🚗 YOLOv5n 기반 차량 탐지 (선택적 추론)
- 📉 모션 감지 + 프레임 간격 최적화 (8FPS)
- 🔔 **사용자 조절 가능한 사운드 알림 (pygame 사용)**
- 🧾 감지 기록 자동 저장 및 로그 확인 기능
- 🖱️ ROI 점 이동, 삭제, 시각화(점선) UI 지원
- 📁 GUI에서 직접 로그 폴더 열기, 감지 시작/종료 제어

---

## 🛠️ 설치 방법

```bash
# 가상환경 권장
python -m venv venv
venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

**requirements.txt 예시**
```text
PyQt5
pygame
opencv-python
ultralytics
```

---

## ▶️ 사용 방법

### 1. ROI 설정
```bash
python src/ROI_Four_Dots.py
```
- 마우스로 점 4개를 찍어 감지 영역 설정
- Ctrl+Z: 마지막 점 삭제
- Ctrl+S 또는 ESC: 저장 및 종료

### 2. 제어 GUI 실행
```bash
python src/Control_GUI.py
```
- 감지 시작/중지 버튼 제공
- 사운드 볼륨 조절 슬라이더
- ROI 표시 On/Off
- 로그 폴더 열기

---

## 🔊 알림음 설정

- `resources/sounds/alert.mp3` 경로에 사운드 파일을 넣어주세요.
- GUI 내 슬라이더로 실시간 볼륨 조절 가능

---

## 📁 폴더 구조

```
Car_Detection/
├── src/
│   ├── Control_GUI.py        ← 메인 제어 GUI
│   ├── ROI_Four_Dots.py      ← ROI 설정 도구
│   ├── VehicleDetector.py    ← 차량 감지 로직
│   ├── alert.py              ← 사운드 + 로그 알림 모듈
│   ├── utils/
│   │   └── ROI_IO.py         ← ROI 불러오기/저장 유틸
│   └── models/
│       └── yolov5n.pt        ← YOLOv5 모델 (직접 다운로드 필요)
├── resources/
│   └── sounds/
│       └── alert.mp3         ← 사용자 알림 사운드
├── logs/                     ← 감지 기록 로그
├── .gitignore
├── README.md
```

---

## 📥 YOLOv5 모델 다운로드

`yolov5n.pt` 파일은 아래 경로에서 받아 `src/models/`에 넣어주세요.

- [YOLOv5 모델 다운로드](https://github.com/ultralytics/yolov5)

---

## 📄 라이선스

이 프로젝트는 **GPLv3** 라이선스를 따릅니다.  
- 소스코드 공개 필요 (상업적 사용 시)
- 포함된 라이브러리: PyQt5, pygame, ultralytics/yolov5 등

---

자세한 예제와 개발 가이드는 👉 [gptonline.ai/ko](https://gptonline.ai/ko/) 에서도 확인하실 수 있습니다!
