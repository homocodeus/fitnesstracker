from angles import joint_angle
from counter import HoldTimer, RepCounter


def test_angles():
    assert abs(joint_angle((1, 0), (0, 0), (0, 1)) - 90) < 1e-6
    assert abs(joint_angle((1, 0), (0, 0), (-1, 0)) - 180) < 1e-6
    assert joint_angle((0, 0), (0, 0), (1, 1)) is None


def feed(c, angles, dt=0.05):
    t = 0.0
    for a in angles:
        c.update(a, t)
        t += dt
    return t


def test_full_rep_counts_once():
    c = RepCounter(90, 160)
    feed(c, [170] * 5 + [80] * 5 + [170] * 5)
    assert c.count == 1


def test_jitter_at_threshold_no_double_count():
    c = RepCounter(90, 160)
    feed(c, [170] * 5 + [80] * 5 + [159, 161, 159, 161, 158] * 4 + [170] * 5)
    assert c.count == 1


def test_noise_spikes_ignored():
    c = RepCounter(90, 160, min_frames=3)
    feed(c, [170] * 5 + [80, 170, 80, 170] + [170] * 5)
    assert c.count == 0


def test_too_fast_rep_rejected():
    c = RepCounter(90, 160, min_frames=1, min_rep_time=1.0)
    feed(c, [170, 80, 170, 80, 170], dt=0.1)
    assert c.count == 1


def test_hold_timer_with_grace():
    h = HoldTimer(160, 185, grace=0.3)
    t = feed(h, [170] * 20 + [100] * 2 + [170] * 20 + [100] * 10, dt=0.1)
    assert not h.holding
    assert abs(h.best - 4.1) < 1e-6  # Ausreißer bei 2.0-2.1s überbrückt
