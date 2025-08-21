short answer: start stupid-simple, but lay **just enough** structure so refactoring is painless. build a tiny, hand‑coded vertical slice first (one emitter, 2–3 receivers, constant‑velocity), using **pure functions + small dataclasses**. once that works and has tests, wrap the same functional core in light OO “facades” if/when you need polymorphism (multiple motion models, waveforms, channels).

here’s a practical plan that keeps you fast now and extensible later.

# phase A — functional core (now)

**why:** easiest to debug, unit‑testable, zero class bloat, perfect for “reps”.

* files:

  * `sim/geometry.py` — pure math: ranges, LOS, doppler.
  * `sim/motion.py` — *callables* for trajectories.
  * `sim/models.py` — tiny dataclasses for state containers.
* conventions:

  * SI units everywhere; time in seconds; vectors as `(x,y,z)`.
  * **immutable** dataclasses (frozen=True) to prevent side‑effects.

**minimal types**

```python
# sim/models.py
from dataclasses import dataclass
import numpy as np
from typing import Callable

Vec3 = np.ndarray         # shape (3,)
TrajFn = Callable[[np.ndarray], np.ndarray]   # t -> (len(t),3)

@dataclass(frozen=True)
class Emitter:
    traj: TrajFn          # position over time
    vel: TrajFn           # velocity over time

@dataclass(frozen=True)
class Receiver:
    traj: TrajFn
    vel: TrajFn
    name: str = "rx"

@dataclass(frozen=True)
class Scenario:
    t: np.ndarray         # sample times
    emitter: Emitter
    receivers: tuple[Receiver, ...]
    fc: float             # Hz
    Fs: float             # Hz
```

**geometry functions (pure)**

```python
# sim/geometry.py
import numpy as np
c = 299_792_458.0

def range_series(ps_t: np.ndarray, pr_t: np.ndarray) -> np.ndarray:
    return np.linalg.norm(ps_t - pr_t, axis=1)

def los_series(ps_t: np.ndarray, pr_t: np.ndarray) -> np.ndarray:
    r = range_series(ps_t, pr_t)[:, None]
    return (ps_t - pr_t) / r

def doppler_series(fc: float, vr_t: np.ndarray, los_t: np.ndarray) -> np.ndarray:
    # vr_t: receiver velocity (len(t),3)
    return -(fc/c) * np.sum(vr_t * los_t, axis=1)
```

**motion as callables (no classes yet)**

```python
# sim/motion.py
import numpy as np

def const_vel(p0, v):
    p0 = np.asarray(p0); v = np.asarray(v)
    def pos(t): return p0[None,:] + t[:,None]*v[None,:]
    def vel(t): return np.repeat(v[None,:], len(t), axis=0)
    return pos, vel

def circle_xy(center, radius, w, z=0.0):
    cx, cy = center
    def pos(t):
        return np.stack([cx + radius*np.cos(w*t),
                         cy + radius*np.sin(w*t),
                         np.full_like(t, z)], axis=1)
    def vel(t):
        return np.stack([-radius*w*np.sin(w*t),
                          radius*w*np.cos(w*t),
                          np.zeros_like(t)], axis=1)
    return pos, vel
```

**why this works:** you can compose anything by swapping functions; tests are trivial (feed `t`, check outputs). when you add satellites later, it’s “just another `TrajFn`”.

**definition of done for A:**

* you can instantiate `Scenario`, compute `r_i(t)`, `τ_i(t)=r_i/c`, `f_{d,i}(t)`, and print/plot GT Δτ/Δf per pair.
* a couple of pytest tests validate symmetry (Δτ\_ij = −Δτ\_ji) and zero‑FDOA for static cases.

# phase B — wrap in thin OO (when you *need* polymorphism)

**trigger conditions:** you want plug‑and‑play components (e.g., `Receiver` can be “aircraft” or “LEO” without changing callers) or you’re adding behaviors (e.g., per‑receiver clock model, antenna patterns).

* introduce **Protocols** (interfaces) rather than deep inheritance.

```python
from typing import Protocol

class Kinematics(Protocol):
    def position(self, t: np.ndarray) -> np.ndarray: ...
    def velocity(self, t: np.ndarray) -> np.ndarray: ...

class Waveform(Protocol):
    def synthesize(self, t: np.ndarray) -> np.ndarray: ...

class Channel(Protocol):
    def render(self, s: np.ndarray, tau: np.ndarray, fd: np.ndarray, Fs: float) -> np.ndarray: ...
```

* then let `Emitter/Receiver` hold a `Kinematics` object; your existing functional implementations can be adapted via tiny adapter classes. the **core math stays pure**.

# phase C — don’t do this (yet)

* no deep class hierarchies (`AircraftReceiver` → `Jet` → `B737`…). you’ll fight subclass explosions.
* no “god” objects orchestrating everything; keep orchestration in a simple `run_sim.py` that wires pure functions.

# what to code today (2–3 hours of productive work)

1. build `sim/models.py`, `sim/motion.py`, `sim/geometry.py` as above.
2. write `experiments/00_smoke.py` that:

   * makes `t = np.arange(N)/Fs`, one emitter at origin, two receivers const‑vel.
   * computes r/τ/f\_d per RX and prints Δτ\_12, Δf\_12 (first and median over t).
3. add two pytest tests (symmetry; zero‑FDOA static).
4. only after this, move to waveform+channel rendering.

# why this path

* **fast feedback:** you’ll see numbers match intuition before any class design.
* **refactorable:** functional core with small dataclasses adapts cleanly to OO facades.
* **testable:** pure functions ⇒ deterministic, easy to unit test and profile.
