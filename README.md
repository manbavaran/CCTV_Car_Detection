# 차량 감지 시스템 (CCTV 기반)

이 프로젝트는 경비원 분들을 위한 **CCTV 차량 감지 도우미 프로그램**입니다.  
PyQt 기반 GUI로 구성되어 있으며, OBS 가상카메라를 통해 CCTV 프로그램 화면을 분석하고 차량이 감지되면 알림을 발생시킵니다.

---

## 📦 주요 기능

- ✅ ROI(관심 영역) 설정 및 저장
- ✅ 차량 감지 (YOLOv5 + 모션 필터링)
- ✅ 사용자 알림 (사운드, 로그 기록)
- ✅ GUI 제어판 (PyQt)
- ✅ 감지 볼륨 / 알림 지속시간 설정
- ✅ 로그 자동 분류 저장
- ✅ 향후: 프로필 관리, 탭 UI, 고급 설정 기능 확장 예정

---

## 🛠️ 설치 방법

```bash
pip install -r requirements.txt
```

> `pygame`, `PyQt5`, `ultralytics`, `opencv-python` 등 필요 패키지가 포함되어 있습니다.

---

## 🚀 사용법

1. `ROI 설정` 탭에서 차량이 감지될 영역 4점을 설정합니다.
2. `제어 GUI`를 실행하여 감지를 시작합니다.
3. 차량이 ROI에 감지되면 소리와 로그가 발생합니다.

---

## 📂 폴더 구조

```
src/
├── profiles/              # 프로필별 ROI 저장
├── utils/                 # 알림, ROI, 로그 모듈 등
│   ├── alert.py
│   ├── ROI_IO.py
│   ├── logger.py
├── Control_GUI.py         # 제어판 GUI
├── Select_Profile.py      # 프로필 선택 화면 (PyQt)
├── VehicleDetector.py     # 차량 감지 로직
```

---

## 📌 라이선스

- YOLOv5 모델은 [Ultralytics](https://github.com/ultralytics/yolov5) MIT 라이선스를 따릅니다.
- 본 프로젝트는 비상업적 목적으로 자유롭게 사용 가능하며, 소스코드 공개 조건 하에 상업적 사용도 가능합니다.

---

✅ 작성일: 2025-06-11  
🔁 이후 업데이트 시 README도 함께 갱신해 주세요.
