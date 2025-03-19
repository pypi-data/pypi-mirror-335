from typing import Callable, Dict, Set
from collections import defaultdict
from tkinter import Misc
from threading import Thread
from keyboard import is_pressed
from time import sleep


class FunctionRegistry:
    def __init__(self) -> None:
        self.registry: Dict[str, Set[Callable]] = defaultdict(set)

    def register(self, key: str) -> Callable[[Callable], Callable]:
        def wrapper(func: Callable) -> Callable:
            self.registry[key].add(func)
            return func
        return wrapper

    def call(self, key: str, *args, **kwargs) -> None:
        for func in self.registry.get(key, set()):
            func(*args, **kwargs)


def tkAfterIdle(root: Misc):
    def wrapper(func: Callable) -> Callable:
        return lambda: root.after_idle(func)
    return wrapper


class KeyBinder:
    def __init__(self):
        self.bindings: Dict[str, Callable] = {}
        self.running = True
        self.thread = Thread(target=self._monitor_keys, daemon=True)

    def bind_to_key(self, keyBind: str, func: Callable):
        self.bindings[keyBind] = func

        if not self.thread.is_alive():
            self.thread.start()

    def _monitor_keys(self):
        while self.running:
            for key, func in self.bindings.items():
                if is_pressed(key):
                    timeWaited = 0
                    timeLimit = 2

                    while is_pressed(key):
                        sleep(0.01)  # Debounce
                        timeWaited += 0.01

                    if timeWaited < timeLimit:
                        func()

            sleep(0.01)  # Reduce CPU usage

    def stop(self):
        self.running = False


key_binder = KeyBinder()


def bindToKey(keyBind: str):
    def inner(func: Callable, *args, **kwargs):
        key_binder.bind_to_key(keyBind, func)
    return inner


__all__ = ["FunctionRegistry", "tkAfterIdle", "bindToKey"]

if __name__ == '__main__':
    test = FunctionRegistry()

    @test.register("a")
    def function():
        print("Function 'do' called.")

    test.call("a")
    test.call("b")

    @bindToKey("Alt+F2")
    def function2():
        print("HELLO!")

    try:
        while True:
            sleep(1)

    except KeyboardInterrupt:
        key_binder.stop()
