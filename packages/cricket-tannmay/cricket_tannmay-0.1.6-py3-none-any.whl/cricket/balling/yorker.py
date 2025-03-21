import cv2


def detect_yorker(frame, ball_color_hsv_range):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, ball_color_hsv_range[0], ball_color_hsv_range[1])
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        ball_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(ball_contour) > 50:
            x, y, w, h = cv2.boundingRect(ball_contour)
            if y > frame.shape[0] * 0.75:  # Ball lands near the batsman's foot
                return "Yorker"
    return "Not a Yorker"


def analyze_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    cap = cv2.VideoCapture(video_path)
    analysis = {}
    frame_idx = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            classification = detect_yorker(frame, ball_color_hsv_range)
            analysis[frame_idx] = classification
            frame_idx += 1

    finally:
        cap.release()

    return analysis


def classify_entire_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    analysis = analyze_video(video_path, ball_color_hsv_range)

    yorker_count = sum(1 for v in analysis.values() if v == "Yorker")
    not_yorker_count = sum(1 for v in analysis.values() if v == "Not a Yorker")
    total_frames = len(analysis)

    if total_frames == 0:
        return "No Valid Frames Detected"

    if yorker_count / total_frames >= 0.5:
        return "Good Yorker"
    elif not_yorker_count / total_frames >= 0.5:
        return "Bad Yorker"
    else:
        return "Not a Yorker"
