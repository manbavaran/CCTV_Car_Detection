import cv2
import json
import os
import re
import PySimpleGUI as sg

# 🪟 GUI로 프로필 이름과 메모 입력받기
def get_profile_info():
    sg.theme('SystemDefault')
    layout = [
        [sg.Text("프로필 이름 (영문/숫자/언더바만):")],
        [sg.Input(key="-NAME-")],
        [sg.Text("이 화면에 대한 설명 메모 (예: 정문 CCTV 야간용):")],
        [sg.Input(key="-MEMO-")],
        [sg.Button("확인"), sg.Button("취소")]
    ]

    window = sg.Window("프로필 정보 입력", layout)
    name, memo = None, None

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "취소"):
            break
        elif event == "확인":
            raw = values["-NAME-"].strip()
            memo_raw = values["-MEMO-"].strip()
            if re.match(r'^[a-zA-Z0-9_]+$', raw):
                name = raw
                memo = memo_raw or "설명 없음"
                break
            else:
                sg.popup("⚠️ 영문, 숫자, 언더바(_)만 입력 가능합니다.", title="입력 오류")

    window.close()
    return name, memo

# 👉 프로필 이름과 설명 메모 입력
profile_name, memo = get_profile_info()
if not profile_name:
    print("사용자 취소 또는 잘못된 입력으로 종료됨.")
    exit()

save_path = f"profiles/{profile_name}.json"
os.makedirs("profiles", exist_ok=True)

# 📷 가상카메라 영상 입력
cap = cv2.VideoCapture(0)
assert cap.isOpened(), "카메라를 열 수 없습니다."

points = []

# 🖱️ 마우스 클릭 처리
def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))

cv2.namedWindow("Set ROI")
cv2.setMouseCallback("Set ROI", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()

    for i, (x, y) in enumerate(points):
        cv2.circle(display, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(display, f"{i+1}", (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if len(points) == 4:
        for i in range(4):
            cv2.line(display, points[i], points[(i+1)%4], (255, 0, 0), 2)

    cv2.putText(display, "ESC: 저장 / Z: 마지막 점 취소", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Set ROI", display)
    key = cv2.waitKey(1)

    if key == 27:
        break
    elif key == ord('z') and points:
        removed = points.pop()
        print(f"❌ 마지막 점 취소: {removed}")

cap.release()
cv2.destroyAllWindows()

# 💾 ROI 좌표와 메모 저장
if len(points) == 4:
    h, w = frame.shape[:2]
    normalized = [[round(x/w, 5), round(y/h, 5)] for (x, y) in points]

    result = {
        "memo": memo,
        "roi": normalized
    }

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[✔] ROI 좌표 및 메모 저장 완료: {save_path}")
else:
    print("[!] 저장 실패: 4개의 점을 찍지 않았습니다.")