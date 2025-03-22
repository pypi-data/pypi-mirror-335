from typing import Optional, Callable, Any, Union
import time

class TimeIt:
    """
    Times the execution of a code block
    : param on_enter: 0 argument callable to call before entering the block
    : param on_exit: 1 argument callable to call before exiting the block
    : param logger: logger class to use
    : param tag: logger tag to print in lag statement
    : param level: logging level to use (default: 'INFO')

    To log a block one can provide:
    A) An on_enter and/or on_exit callable(s)
    B) A logger object
    C) A tag

    Precedence rule:
    1) If either (or both) on_enter and on_exit are provided, they supercede all other arguments
    2) If no callable is provided, the default functions are used
    3) If no logger is provided, the log is printed using print()
    4) If no tag is provided, nothing will be logged

    Example:
    >>> with TimeIt(
    ...     on_enter=lambda: self.logger.info('Starting operation'),
    ...     on_exit=lambda t: self.logger.info('Operation completed in {:.6f} seconds'.format(t))
    ...):
    ...     # <code block>
    ...     pass
    Output:
        Starting operation
        Operation completed in 0.000008 seconds


    >>> with TimeIt(
    ...     logger=domain.logger_service.default_logger,
    ...     tag = 'Operation DoThatThing'
    ...):
    ...     # <code block>
    ...     pass
    Output:
        Starting <Operation DoThatThing>
        <Operation DoThatThing> took 0.000008 seconds

    >>> with TimeIt() as timeit:
    ...     # <code block>
    ...     pass
    >>> timeit.time_elapsed
    Output:
        8.106e-06
    """

    def __init__(
        self,
        on_enter: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[float], None]] = None,
        logger: Optional[Any] = None,
        tag: Optional[str] = None,
        level: str = 'INFO'
    ) -> None:
        self._on_enter = on_enter
        self._on_exit = on_exit
        self._logger = logger
        self._tag = tag
        self._level = None
        self._time: Optional[float] = None

        if self._on_enter:
            if not callable(self._on_enter):
                raise TypeError("on_enter must be a callable")
            if hasattr(self._on_enter, "__code__"):
                if self._on_enter.__code__.co_argcount != 0:
                    raise ValueError("on_enter must have 0 arguments")

        if self._on_exit:
            if not callable(self._on_exit):
                raise TypeError("on_exit must be a callable")
            if hasattr(self._on_exit, "__code__"):
                if self._on_exit.__code__.co_argcount != 1:
                    raise ValueError("on_exit must have 1 argument")

        if not (self._on_enter or self._on_exit) and self._tag is not None:
            if not isinstance(level, str):
                raise TypeError("level must be a string")
            self._level = level.upper()

            if self._logger:
                self._on_enter = self._default_enter
                self._on_exit = self._default_exit
            else:
                self._on_enter = self._print_enter
                self._on_exit = self._print_exit
        
    def _default_enter(self) -> None:
        """Default enter logging using provided logger."""
        if self._logger and self._tag:
            self._logger.log(f'Starting <{self._tag}>', level_string=self._level)

    def _default_exit(self, t: float) -> None:
        """Default exit logging using provided logger."""
        if self._logger and self._tag:
            self._logger.log(f'<{self._tag}> took {t:.6f} seconds', level_string=self._level)

    def _print_enter(self) -> None:
        """Default enter logging using print."""
        if self._tag:
            print(f'Starting <{self._tag}>')

    def _print_exit(self, t: float) -> None:
        """Default exit logging using print."""
        if self._tag:
            print(f'<{self._tag}> took {t:.6f} seconds')

    @property
    def time_elapsed(self) -> Optional[float]:
        """Returns the elapsed time of the last execution."""
        return self._time
    
    def __enter__(self) -> 'TimeIt':
        if self._on_enter:
            self._on_enter()
        self._time = time.time()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        self._time = time.time() - self._time
        if self._on_exit:
            self._on_exit(self._time)
        if exc_type is not None:
            return False
        return True