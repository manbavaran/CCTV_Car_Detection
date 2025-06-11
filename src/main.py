import numpy as np
from Select_Profile import select_profile
from Big_Filtering import run_detection

def main():
    # 1. GUI로부터 프로필 선택 및 ROI 정보 로딩
    profile_name, roi_data = select_profile()

    if profile_name and roi_data:
        # 2. ROI 좌표를 정수 픽셀 좌표로 변환 (640x480 기준)
        roi_points = np.array([[int(x * 640), int(y * 480)] for x, y in roi_data["roi"]])

        # 3. 감지 루프 실행
        run_detection(profile_name, roi_points)
    else:
        print("[!] 프로필 선택 또는 ROI 로딩 실패")

if __name__ == "__main__":
    main()