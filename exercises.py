"""Übungsdefinitionen: Gelenk-Landmarks + Winkelbereiche."""

# MediaPipe Pose Landmark-Indizes
L_SHOULDER, R_SHOULDER = 11, 12
L_ELBOW, R_ELBOW = 13, 14
L_WRIST, R_WRIST = 15, 16
L_HIP, R_HIP = 23, 24
L_KNEE, R_KNEE = 25, 26
L_ANKLE, R_ANKLE = 27, 28

EXERCISES = {
    "curl": {
        "name": "Bizeps-Curl",
        "type": "reps",
        "joints": {"L": (L_SHOULDER, L_ELBOW, L_WRIST), "R": (R_SHOULDER, R_ELBOW, R_WRIST)},
        "down": 50, "up": 150,     # gebeugt <= 50°, gestreckt >= 150°
    },
    "squat": {
        "name": "Kniebeuge",
        "type": "reps",
        "joints": {"L": (L_HIP, L_KNEE, L_ANKLE), "R": (R_HIP, R_KNEE, R_ANKLE)},
        "down": 100, "up": 160,
    },
    "pushup": {
        "name": "Liegestütz",
        "type": "reps",
        "joints": {"L": (L_SHOULDER, L_ELBOW, L_WRIST), "R": (R_SHOULDER, R_ELBOW, R_WRIST)},
        "down": 90, "up": 155,
    },
    "plank": {
        "name": "Plank (Halten)",
        "type": "hold",
        "joints": {"L": (L_SHOULDER, L_HIP, L_ANKLE), "R": (R_SHOULDER, R_HIP, R_ANKLE)},
        "lo": 160, "hi": 185,      # Körper gerade
    },
    "wallsit": {
        "name": "Wandsitz (Halten)",
        "type": "hold",
        "joints": {"L": (L_HIP, L_KNEE, L_ANKLE), "R": (R_HIP, R_KNEE, R_ANKLE)},
        "lo": 75, "hi": 110,
    },
}
