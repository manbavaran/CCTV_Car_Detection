import PySimpleGUI as sg
import os
import json
import subprocess

def select_profile(profile_dir="profiles"):
    os.makedirs(profile_dir, exist_ok=True)
    profiles = []

    # 프로필 목록 로드
    def load_profiles():
        result = []
        for file in os.listdir(profile_dir):
            if file.endswith(".json"):
                filepath = os.path.join(profile_dir, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        memo = data.get("memo", "설명 없음")
                        name = file.replace(".json", "")
                        result.append((f"{name} - {memo}", name))
                except Exception as e:
                    print(f"[!] JSON 로드 실패: {file}, {e}")
        return result

    profiles = load_profiles()

    layout = [
        [
            sg.Listbox(
                values=[p[0] for p in profiles],
                size=(40, 12),
                key="-PROFILE-",
                enable_events=True,
                enable_double_click_events=True
            ),
            sg.Column([
                [sg.Button("추가", size=(8, 1))],
                [sg.Button("삭제", size=(8, 1))]
            ])
        ],
        [sg.Button("확인", size=(10, 1)), sg.Button("종료", size=(10, 1))]
    ]

    window = sg.Window("프로필 선택 및 관리", layout)
    selected_profile = None
    selected_roi_data = None

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "종료"):
            break

        elif event == sg.EVENT_LISTBOX_DOUBLE_CLICKED:
            if values["-PROFILE-"]:
                display_name = values["-PROFILE-"][0]
                selected_profile = next((p[1] for p in profiles if p[0] == display_name), None)
                break

        elif event == "추가":
            window.hide()
            subprocess.run(["python", "ROI_Four_Dots.py"])
            profiles = load_profiles()
            window["-PROFILE-"].update([p[0] for p in profiles])
            window.un_hide()

        elif event == "삭제":
            if values["-PROFILE-"]:
                display_name = values["-PROFILE-"][0]
                internal_name = next((p[1] for p in profiles if p[0] == display_name), None)
                if internal_name:
                    confirm = sg.popup_yes_no(f"'{internal_name}' 프로필을 삭제할까요?")
                    if confirm == "Yes":
                        os.remove(os.path.join(profile_dir, internal_name + ".json"))
                        profiles = load_profiles()
                        window["-PROFILE-"].update([p[0] for p in profiles])
            else:
                sg.popup("삭제할 프로필을 선택하세요.")

        elif event == "확인":
            if values["-PROFILE-"]:
                display_name = values["-PROFILE-"][0]
                selected_profile = next((p[1] for p in profiles if p[0] == display_name), None)
                break
            else:
                sg.popup("프로필을 선택하세요.")

    window.close()

    # ROI 좌표 자동 로딩
    if selected_profile:
        roi_path = os.path.join(profile_dir, selected_profile + ".json")
        try:
            with open(roi_path, "r", encoding="utf-8") as f:
                selected_roi_data = json.load(f)
            print(f"[✔] 선택된 프로필: {selected_profile}")
            print(f"[✔] ROI 좌표 로드 완료: {selected_roi_data['roi']}")
            return selected_profile, selected_roi_data
        except Exception as e:
            print(f"[!] ROI 로딩 실패: {e}")

    return None, None
