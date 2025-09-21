import time
from math import sin, pi, pow
from typing import Callable

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget

def _out_sine(x) -> float:
    return sin((x * pi) / 2)

def _out_cubic(x) -> float:
    return 1 - ((1 - x)**3)

def _out_quart(x) -> float:
    return 1 - pow(1 - x, 4)

def _out_circ(x) -> float:
    return 1 - ((1 - x)**3)  #sqrt(1 - pow(x - 1, 2))


class Animation:
    easeOutSine: Callable = _out_sine
    easeOutCubic: Callable = _out_cubic
    easeOutQuart: Callable = _out_quart
    easeOutCirc: Callable = _out_sine



class AnimationHandler:
    def __init__(self, widget: QWidget, startv: int, endv: int, type: Callable) -> None:
        self.widget: QWidget = widget
        self.type: Callable = type

        self.startv: int = startv
        self.endv: int = endv

        self.value: float = 0
        self.orgstart_time: float = 0
        self.speed: float = 3.45

        self.sensitivity: float = 0.001

        self.reverse: bool = False
        self.loop: bool = False
        self.started = None

        self._tickfunc: Callable | None = None

    def tick(self, func: Callable) -> Callable:
        self._tickfunc = func
        return func

    def start(self, reverse=False, loop=False) -> None:
        self.reverse = reverse
        self.loop = loop
        self.started = True
        self.orgstart_time = time.time()
        self.value = 0
        self.widget.update()

    def reset(self) -> None:
        self.value = 0
        self.started = None

    def done(self) -> bool:
        return self.started is None

    def update(self) -> None:
        if not self.done():
            ep: float = time.time() - self.orgstart_time

            self.value = self.type(ep * self.speed)

            if self.reverse:
                if self.current() <= self.startv + self.sensitivity:
                    self.started = None
            else:
                if self.current() >= self.endv - self.sensitivity:
                    self.started = None

            if self.done():
                if self.loop:
                    self.start(reverse=not self.reverse, loop=True)
                return

            #print(self.value)
            if self._tickfunc:
                self._tickfunc()

    def current(self) -> float:
        if self.reverse:
            return self.endv - (self.value * (self.endv - self.startv))
        else:
            return self.value * (self.endv - self.startv)

    def lerp(self, a: QColor, b: QColor) -> QColor:
        f: float = self.current() / self.endv
        r1, r2 = a.red(),   b.red()
        g1, g2 = a.green(), b.green()
        b1, b2 = a.blue(),  b.blue()
        a1, a2 = a.alpha(), b.alpha()

        r  = (r2 - r1) * f + r1
        g  = (g2 - g1) * f + g1
        _b = (b2 - b1) * f + b1
        _a = (a2 - a1) * f + a1

        return QColor(int(r), int(g), int(_b), int(_a))

    def lerp_f(self, a: float, b: float) -> float:
        f: float = self.current() / self.endv
        return (b - a) * f + a
