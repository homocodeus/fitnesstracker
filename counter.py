"""Zustandsbasierte Wiederholungszählung und Haltezeitmessung."""
from dataclasses import dataclass, field


@dataclass
class RepCounter:
    """Zustandsautomat: UP <-> DOWN mit Hysterese.

    Eine Wiederholung zählt nur bei vollständigem Zyklus UP -> DOWN -> UP.
    Schutz gegen Mehrfachzählung:
      * Hysterese: getrennte Schwellwerte (down_thresh < up_thresh), dazwischen
        bleibt der Zustand unverändert -> kein Flattern an einer Grenze.
      * min_frames: neuer Zustand muss N Frames stabil sein (Entprellung).
      * min_rep_time: Mindestdauer pro Wiederholung in Sekunden.
    """
    down_thresh: float          # Winkel <= down_thresh  -> Zustand DOWN
    up_thresh: float            # Winkel >= up_thresh    -> Zustand UP
    min_frames: int = 3
    min_rep_time: float = 0.5
    count: int = 0
    state: str = "UP"
    _candidate: str = field(default=None, repr=False)
    _cand_frames: int = field(default=0, repr=False)
    _last_rep_t: float = field(default=-1e9, repr=False)
    _reached_down: bool = field(default=False, repr=False)

    def update(self, angle, t):
        if angle is None:
            return self.count
        if angle <= self.down_thresh:
            target = "DOWN"
        elif angle >= self.up_thresh:
            target = "UP"
        else:
            target = self.state  # Hysteresebereich: kein Wechsel
            self._candidate, self._cand_frames = None, 0

        if target != self.state:
            if target == self._candidate:
                self._cand_frames += 1
            else:
                self._candidate, self._cand_frames = target, 1
            if self._cand_frames >= self.min_frames:
                self._transition(target, t)
        return self.count

    def _transition(self, new_state, t):
        self.state = new_state
        self._candidate, self._cand_frames = None, 0
        if new_state == "DOWN":
            self._reached_down = True
        elif new_state == "UP" and self._reached_down:
            self._reached_down = False
            if t - self._last_rep_t >= self.min_rep_time:
                self.count += 1
                self._last_rep_t = t


@dataclass
class HoldTimer:
    """Misst Haltezeit, solange der Winkel im Bereich [lo, hi] liegt.

    grace: kurze Ausreißer (Sekunden) unterbrechen das Halten nicht.
    """
    lo: float
    hi: float
    grace: float = 0.3
    total: float = 0.0
    best: float = 0.0
    _start: float = field(default=None, repr=False)
    _last_in: float = field(default=None, repr=False)

    @property
    def holding(self):
        return self._start is not None

    def current(self, t):
        return (t - self._start) if self._start is not None else 0.0

    def update(self, angle, t):
        inside = angle is not None and self.lo <= angle <= self.hi
        if inside:
            if self._start is None:
                self._start = t
            self._last_in = t
        elif self._start is not None and t - self._last_in > self.grace:
            dur = self._last_in - self._start
            self.total += dur
            self.best = max(self.best, dur)
            self._start = self._last_in = None
        return self.current(t)
