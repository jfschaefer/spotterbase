import signal
from typing import Callable, Any


class SignalDelayManager:
    """ A very hacky implementation to delay signals to ensure that crucial operations can finish undisturbed.
        I'm fairly sure that not all edge cases have been covered
    """

    def __init__(self, signals_to_delay: list[signal.Signals]):
        self._signals_to_delay = signals_to_delay
        self._already_entered = False

    def __enter__(self):
        assert not self._already_entered, 'Already in context'
        self._already_entered = True

        def handle(sig, s, f):
            if self._exit_started:
                self._old_handlers[sig](s, f)
            else:
                self._calls_on_exit.append(lambda: self._old_handlers[sig](s, f))

        self._calls_on_exit: list[Callable] = []
        self._old_handlers: dict[signal.Signals, Any] = {}
        self._exit_started = False
        for sig in self._signals_to_delay:
            self._old_handlers[sig] = signal.getsignal(sig)

            def concrete_handler(s, f, sig=sig):
                handle(sig, s, f)

            signal.signal(sig, concrete_handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_started = True
        for call in self._calls_on_exit:
            call()
        for s, h in self._old_handlers.items():
            signal.signal(s, h)
        self._already_entered = False


DefaultSignalDelay = \
    lambda: SignalDelayManager(signals_to_delay=[signal.Signals.SIGINT, signal.Signals.SIGTERM])  # noqa: E731
