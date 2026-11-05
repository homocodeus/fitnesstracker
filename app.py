"""Echtzeit-Bewegungsanalyse mit Webcam + MediaPipe Pose Landmarker.

Start:  python app.py --exercise squat [--camera 0]
Tasten: 1-5 Übung wechseln, r Reset, q/ESC Beenden
"""
import argparse
import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

from angles import EmaFilter, joint_angle
from counter import HoldTimer, RepCounter
from exercises import EXERCISES

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pose_landmarker_full.task")
MIN_VISIBILITY = 0.5

CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24),
               (23, 24), (23, 25), (25, 27), (24, 26), (26, 28)]


def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Lade Pose-Modell herunter ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


class Session:
    def __init__(self, key):
        self.key = key
        self.ex = EXERCISES[key]
        self.filter = EmaFilter(0.4)
        if self.ex["type"] == "reps":
            self.tracker = RepCounter(self.ex["down"], self.ex["up"])
        else:
            self.tracker = HoldTimer(self.ex["lo"], self.ex["hi"])

    def side_angle(self, lms):
        """Wählt die besser sichtbare Körperseite und berechnet deren Winkel."""
        best, best_vis = None, MIN_VISIBILITY
        for a, b, c in self.ex["joints"].values():
            vis = min(lms[i].visibility for i in (a, b, c))
            if vis >= best_vis:
                best_vis = vis
                best = joint_angle(*[(lms[i].x, lms[i].y) for i in (a, b, c)]), (a, b, c)
        return best if best else (None, None)


def draw(frame, lms, session, angle, joints, t):
    h, w = frame.shape[:2]
    if lms:
        pts = {i: (int(l.x * w), int(l.y * h)) for i, l in enumerate(lms)}
        for a, b in CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (200, 200, 200), 2)
        if joints:
            for a, b in zip(joints, joints[1:]):
                cv2.line(frame, pts[a], pts[b], (0, 220, 255), 4)
            if angle is not None:
                cv2.putText(frame, f"{angle:.0f}", (pts[joints[1]][0] + 10, pts[joints[1]][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2)

    cv2.rectangle(frame, (0, 0), (360, 130), (30, 30, 30), -1)
    tr = session.tracker
    lines = [session.ex["name"]]
    if isinstance(tr, RepCounter):
        lines += [f"Wiederholungen: {tr.count}", f"Zustand: {tr.state}"]
    else:
        lines += [f"Aktuell: {tr.current(t):.1f}s", f"Gesamt: {tr.total + tr.current(t):.1f}s  Best: {tr.best:.1f}s"]
    lines.append(f"Winkel: {angle:.0f}" if angle is not None else "Winkel: --")
    for i, s in enumerate(lines):
        cv2.putText(frame, s, (10, 28 + i * 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exercise", default="squat", choices=EXERCISES.keys())
    p.add_argument("--camera", type=int, default=0)
    args = p.parse_args()

    ensure_model()
    options = vision.PoseLandmarkerOptions(
        base_options=mp_tasks.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5)

    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY  # DirectShow unter Windows
    cap = cv2.VideoCapture(args.camera, backend)
    if not cap.isOpened():
        raise SystemExit(f"Kamera {args.camera} konnte nicht geöffnet werden.")

    keys = list(EXERCISES)
    session = Session(args.exercise)
    t0 = time.monotonic()
    last_ts = -1

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            t = time.monotonic() - t0
            ts = max(int(t * 1000), last_ts + 1)  # streng monoton steigend
            last_ts = ts

            rgb = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = landmarker.detect_for_video(rgb, ts)
            lms = result.pose_landmarks[0] if result.pose_landmarks else None

            raw, joints = session.side_angle(lms) if lms else (None, None)
            angle = session.filter.update(raw) if raw is not None else None
            session.tracker.update(angle, t)

            draw(frame, lms, session, angle, joints, t)
            cv2.imshow("Fitness-Tracking", frame)

            k = cv2.waitKey(1) & 0xFF
            if k in (ord("q"), 27):
                break
            if k == ord("r"):
                session = Session(session.key)
            if ord("1") <= k < ord("1") + len(keys):
                session = Session(keys[k - ord("1")])

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
