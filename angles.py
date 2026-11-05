"""Eigene Algorithmen zur Berechnung von Gelenkwinkeln."""
import math


def joint_angle(a, b, c):
    """Winkel am Gelenk b (in Grad, 0..180) zwischen den Segmenten b->a und b->c.

    a, b, c: (x, y) oder (x, y, z) Koordinaten.
    Berechnung über Skalarprodukt: cos(theta) = (BA · BC) / (|BA| |BC|)
    """
    ba = [p - q for p, q in zip(a, b)]
    bc = [p - q for p, q in zip(c, b)]
    dot = sum(x * y for x, y in zip(ba, bc))
    norm = math.sqrt(sum(x * x for x in ba)) * math.sqrt(sum(x * x for x in bc))
    if norm < 1e-9:
        return None
    cos_t = max(-1.0, min(1.0, dot / norm))
    return math.degrees(math.acos(cos_t))


class EmaFilter:
    """Exponentielle Glättung gegen Landmark-Jitter."""

    def __init__(self, alpha=0.4):
        self.alpha = alpha
        self.value = None

    def update(self, x):
        if x is None:
            return self.value
        self.value = x if self.value is None else self.alpha * x + (1 - self.alpha) * self.value
        return self.value
