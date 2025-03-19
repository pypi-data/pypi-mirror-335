import _thread

from .actuators import Actuator
from .low_level import FastBlockingTimer

try:
    from typing import Callable
except Exception:
    print("micropython i guess")


class Robot:
    def __init__(self) -> None:
        self.actuators: list[Actuator] = []
        self.sensors = []

    def set_actuators(self):
        pass


class RunnerThread:
    class CallQueue:
        def __init__(self, _th: "RunnerThread") -> None:
            self.th = _th
            self.calling_queue = []

        def __or__(self, fn: tuple[Callable] | Callable):
            self.calling_queue.append((fn))
            return self

        def __iter__(self):
            """
            Iteration over the calling queue to get all methods in order

            Indirect iteration to allow for dynamic changes to the queue
            during execution
            """
            call_n = 0
            while call_n < len(self.calling_queue):
                yield self.calling_queue[call_n]
                call_n += 1

        def __len__(self):
            return len(self.calling_queue)

        def __sub__(self, fn: int | tuple[Callable] | Callable):
            if isinstance(fn, int):
                self.calling_queue = self.calling_queue[:-fn]
                return self
            self.calling_queue.remove(fn)
            return self

        def __lt__(self, *args):
            self.th.initial_args = args
            return self

    def __init__(
        self,
        period: float = -1,
        frequency: float = -1,
        periodic: bool = None,
    ):
        self.initial_args = []
        self.callback = RunnerThread.CallQueue(self)
        self.timer = FastBlockingTimer(
            period=period, frequency=frequency, periodic=periodic, callback=self._run
        )
        self.thread = None

    def start(self):
        self.timer.running = True
        self.thread = _thread.start_new_thread(self.timer.run, ())

    def _run(self):
        # print(len(self.callback))
        a = self.initial_args
        for call in self.callback:
            a = [call_(*a) for call_ in call] if isinstance(call, tuple) else [call(*a)]

    def __rshift__(self, right):
        return self.callback | right


class Clock(RunnerThread):
    def __init__(self, dt=0.01, t_max=10):
        super().__init__(dt)
        self.t = 0
        self.dt = dt
        self.t_max = t_max
        self.timer.running = False
        self.length = round(self.t_max / self.dt) + 1

    def _run(self):
        a = [self.t]
        for call in self.callback:
            a = [call_(*a) for call_ in call] if isinstance(call, tuple) else [call(*a)]
        self.t += self.dt
        if self.t >= self.t_max:
            self.timer.stop()

    def wait(self):  # will probably be changed to async in the future
        while self.timer.running:
            pass

    def step(self, force=False):
        if not self.timer.running or force:
            a = [self.t]
            for call in self.callback:
                a = (
                    [call_(*a) for call_ in call]
                    if isinstance(call, tuple)
                    else [call(*a)]
                )
            self.t += self.dt
        else:
            raise RuntimeError(
                "Clock is running, are you sure you want to force step from this thread? (you can pass force=True to force step)"
            )
