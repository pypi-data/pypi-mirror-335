from __future__ import annotations
from typing import Union, Literal, get_args
from datetime import datetime, timedelta, time
from abc import ABC, abstractmethod
from random import randrange

from ..misc.doc import doc_category


__all__ = (
    "BaseMessagePeriod",
    "DurationPeriod",
    "EveryXPeriod",
    "FixedDurationPeriod",
    "RandomizedDurationPeriod",
    "DaysOfWeekPeriod",
    "DailyPeriod",
    "NamedDayOfYearPeriod",
    "NamedDayOfMonthPeriod",
)


class BaseMessagePeriod(ABC):
    """
    Base for implementing message periods.
    Subclasses can be passed to ``xMESSAGE``'s ``period`` parameter.
    """
    def __init__(self, next_send_time: Union[datetime, timedelta]) -> None:
        if next_send_time is None:
            next_send_time = datetime.now()
        elif isinstance(next_send_time, timedelta):
            next_send_time = datetime.now() + next_send_time

        next_send_time = next_send_time.astimezone()
        self.next_send_time: datetime = next_send_time
        self.defer(next_send_time)  # Correct the next time to confirm with the period type

    @abstractmethod
    def defer(self, dt: datetime):
        """
        Defers advertising until ``dt``
        This should be used for overriding the normal next datetime
        the message was supposed to be sent on.
        """
        pass

    def get(self) -> datetime:
        "Returns the next datetime the message is going to be sent."
        return self.next_send_time

    @abstractmethod
    def calculate(self) -> datetime:
        "Calculates the next datetime the message is going to be sent."
        pass

    @abstractmethod
    def adjust(self, minimum: timedelta) -> None:
        """
        Adjust the period to always be greater than the ``minimum``.
        """
        pass

class DurationPeriod(BaseMessagePeriod):
    """
    Base for duration-like message periods.
    """
    @abstractmethod
    def _get_period(self) -> timedelta:
        "Get's the calculated relative period (offset) from previous scheduled time."
        pass

    def defer(self, dt: datetime):
        while (self.next_send_time) < dt:
            self.calculate()

    def calculate(self):
        current_stamp = datetime.now().astimezone()
        duration = self._get_period()
        while self.next_send_time < current_stamp:
            self.next_send_time += duration

        return self.next_send_time

class EveryXPeriod(BaseMessagePeriod):
    """
    Base for every-x-like message periods.
    The X can be Day, Month, Year, ...
    """
    def defer(self, dt: datetime):
        self.next_send_time = dt
        self.calculate()


@doc_category("Message period")
class FixedDurationPeriod(DurationPeriod):
    """
    A fixed message (sending) period.

    Parameters
    ---------------
    duration: timedelta
        The period duration (how much time to wait after every send).
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.
    """
    def __init__(self, duration: timedelta, next_send_time: Union[datetime, timedelta]  = None) -> None:
        self.duration = duration
        super().__init__(next_send_time)

    def _get_period(self):
        return self.duration

    def adjust(self, minimum: timedelta) -> None:
        self.duration = max(minimum, self.duration)


@doc_category("Message period")
class RandomizedDurationPeriod(DurationPeriod):
    """
    A randomized message (sending) period.
    After every send, the message will wait a different randomly
    chosen period within ``minimum`` and ``maximum``.

    Parameters
    --------------
    minimum: timedelta
        Bottom limit of the randomized period.
    maximum: timedelta
        Upper limit of the randomized period.
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.
    """
    def __init__(
        self,
        minimum: timedelta,
        maximum: timedelta,
        next_send_time: Union[datetime, timedelta]  = None
    ) -> None:
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(next_send_time)


    def _get_period(self):
        return timedelta(seconds=randrange(self.minimum.total_seconds(), self.maximum.total_seconds()))

    def adjust(self, minimum: timedelta) -> None:
        if self.minimum >= minimum:
            return

        self.maximum = minimum + (self.maximum - self.minimum)  # Preserve the period band's width
        self.minimum = minimum


@doc_category("Message period")
class DaysOfWeekPeriod(EveryXPeriod):
    """
    Represents a period that will send on ``days`` at specific ``time``.

    E. g., parameters ``days=["Mon", "Wed"]`` and ``time=time(hour=12, minute=0)``
    produce a behavior that will send a message every Monday and Wednesday at 12:00.

    Parameters
    --------------
    days: list[Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
        List of day abbreviations on which the message will be sent.
    time: :class:`datetime.time`
        The time on which the message will be sent (every day of ``days``).
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.

    Raises
    -----------
    ValueError
        The ``days`` parameter was an empty list.
    """
    _WEEK_DAYS = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    WEEK_DAYS = tuple(get_args(_WEEK_DAYS))

    def  __init__(
        self,
        days: list[DaysOfWeekPeriod._WEEK_DAYS],
        time: time,
        next_send_time: Union[datetime, timedelta] = None
    ) -> None:
        if not days:
            raise ValueError(f"'days' parameter must be a list of day literals {DaysOfWeekPeriod.WEEK_DAYS}.")

        if time.tzinfo is None:
            time = time.replace(tzinfo=datetime.now().astimezone().tzinfo)

        self.days = days
        self._days_enum = tuple(set(DaysOfWeekPeriod.WEEK_DAYS.index(day) for day in days))
        self.time = time
        super().__init__(next_send_time)

    def calculate(self):
        # In case of deferral, the next_send_time will be greater,
        # thus next send time should be relative to that instead of now.
        now = max(datetime.now().astimezone(), self.next_send_time)
        now_time = now.timetz()
        self_time = self.time

        if now_time > self_time:
            # If current day already passed, assume the next day
            # to prevent the current day from being selected again
            now += timedelta(days=1)

        # Find next possible day
        now_weekday = now.weekday()
        for day_i in self._days_enum:
            if day_i >= now_weekday:
                next_weekday = day_i
                break
        else:
            next_weekday = self._days_enum[0]

        # In case next_weekday is less than current weekday, add 7.
        # Then do modulus in case it wasn't less.
        offset = (next_weekday - now_weekday + 7) % 7

        now += timedelta(days=offset)
        # Replace the hour of either today / next day and then calculate
        # the difference from current datetime
        next_datetime = now.replace(
            hour=self_time.hour,
            minute=self_time.minute,
            second=self_time.second,
            microsecond=self_time.microsecond,
        )
        self.next_send_time = next_datetime
        return next_datetime

    def adjust(self, minimum: timedelta) -> None:
        # The minium between sends will always be 24 hours.
        # Slow-mode minimum is maximum 6 hours, thus this is not needed.
        pass


@doc_category("Message period")
class DailyPeriod(DaysOfWeekPeriod):
    """
    Represents a daily send period.
    Messages will be sent every day at ``time``.

    Parameters
    --------------
    time: time
        The time on which the message will be sent.
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.
    """
    def __init__(
        self,
        time: time,
        next_send_time: Union[datetime, timedelta]  = None
    ) -> None:
        super().__init__(DaysOfWeekPeriod.WEEK_DAYS, time, next_send_time)


@doc_category("Message period")
class NamedDayOfYearPeriod(EveryXPeriod):
    """
    .. versionadded:: 4.1

    This period type enables messages to be sent on specific ``week`` and ``day`` of a ``month`` each year on
    a specific ``time``.

    E.g., each year on second Monday in December at 12 noon (example below).

    Parameters
    ---------------
    time: time
        The time at which to send.
    day: 'Mon'-'Sun'
        The day of week when to send.
    week: int
        The week number of which to send. E.g., 1 for 1st week, 2 for second week.
    month: 1 - 12
        The month in which to send.
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.

    Example
    ----------
    .. code-block:: python

        #  Every second Monday of December at 12:00.
         NamedDayOfYearPeriod(
            time=time(hour=12),  # Time
            day="Mon",  # Day (Monday)
            week=2,  # Which week (second monday)
            month=12  # Month (December)
        )
    """
    DAYS = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _DAYS_ARGS = get_args(DAYS)

    def __init__(
        self,
        time: time,
        day: NamedDayOfYearPeriod.DAYS,
        week: Literal[1, 2, 3, 4, 5],
        month: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        next_send_time: Union[datetime, timedelta] = None
    ) -> None:
        self.time = time
        self.day = day
        self.week = week
        self.month = month
        self.isoday = NamedDayOfYearPeriod._DAYS_ARGS.index(day) + 1
        super().__init__(next_send_time)

    def calculate(self) -> datetime:
        # In case of deferral, the next_send_time will be greater,
        # thus next send time should be relative to that instead of now.
        now = max(datetime.now().astimezone(), self.next_send_time)
        self_time = self.time
        next = now.replace(
            month=self.month,
            hour=self_time.hour,
            minute=self_time.minute,
            second=self_time.second,
            microsecond=self_time.microsecond
        )

        while True:
            next += timedelta(self.isoday - next.isoweekday())  # Move to the named day (e.g., Monday)
            next += timedelta(days=7 * (self.week - next.day // 7 - 1))  # Move to the specified weekday (e.g., 2nd (Monday))
            if next >= now:
                break

            next = next.replace(year=next.year + 1)

        self.next_send_time = next
        return next

    def adjust(self, minimum: timedelta) -> None:
        pass  # Slow-mode can't be one year long


@doc_category("Message period")
class NamedDayOfMonthPeriod(EveryXPeriod):
    """
    .. versionadded:: 4.1

    This period type enables messages to be sent on specific ``week`` and ``day`` each month at a specific ``time``.

    E.g., each year on second Monday in December at 12 noon (example below).

    Parameters
    ---------------
    time: time
        The time at which to send.
    day: 'Mon'-'Sun'
        The day of week when to send.
    week: int
        The week number of which to send. E.g., 1 for 1st week, 2 for second week.
    next_send_time: datetime | timedelta
        Represents the time at which the message should first be sent.
        Use ``datetime`` to specify the exact date and time at which the message should start being sent.
        Use ``timedelta`` to specify how soon (after creation of the object) the message
        should start being sent.

    Example
    ----------
    .. code-block:: python

        #  Second Monday of every month at 12:00.
         NamedDayOfMonthPeriod(
            time=time(hour=12),  # Time
            day="Mon",  # Day (Monday)
            week=2,  # Which week (second monday)
        )
    """
    DAYS = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _DAYS_ARGS = get_args(DAYS)

    def __init__(
        self,
        time: time,
        day: NamedDayOfMonthPeriod.DAYS,
        week: Literal[1, 2, 3, 4, 5],
        next_send_time: Union[datetime, timedelta] = None
    ) -> None:
        self.time = time
        self.day = day
        self.week = week
        self.isoday = NamedDayOfMonthPeriod._DAYS_ARGS.index(day) + 1
        super().__init__(next_send_time)

    def calculate(self) -> datetime:
        now = max(datetime.now().astimezone(), self.next_send_time)
        self_time = self.time
        next = now.replace(
            hour=self_time.hour,
            minute=self_time.minute,
            second=self_time.second,
            microsecond=self_time.microsecond
        )

        while True:
            next += timedelta(self.isoday - next.isoweekday())  # Move to the named day (e.g., Monday)
            next += timedelta(days=7 * (self.week - next.day // 7 - 1))  # Move to the specified weekday (e.g., 2nd (Monday))
            if next >= now:
                break

            next_month = next.month + 1
            next_year = next.year
            if next_month > 12:
                next_year += 1
                next_month = 1

            next = next.replace(year=next_year, month=next_month)

        self.next_send_time = next
        return next

    def adjust(self, minimum: timedelta) -> None:
        pass  # Slow-mode can't be one month long
