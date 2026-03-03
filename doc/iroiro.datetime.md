# iroiro.datetime

This document describes the API set provided by `iroiro.datetime`.

For the index of this package, see [iroiro.md](iroiro.md).


## Overview

This API set is probably not useful, as the standard `datetime` package completely covers its features.

There are several reasons that made me keep it,

*   I found it silly but interesting writing it dependency-free
*   As a bonus, it could be taken as a reference implementation in other environments
    -   [Vim on Windows doesn't support `strptime()`](https://github.com/vim/vim/issues/19418)


## `weekday(year, month, day)`

Return the day of the week as an integer, Sunday is `0`, Monday is `1`, and Saturday is `6`.

It mimics [`date.isoweekday()`](https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday).


## `is_leap_year(year)`

Return whether `year` is a leap year.


## `to_abs_days(year, month, day)`

Calculate the number of days of the specified `year/month/day` since `0001/01/01`.

Equals to:
```python
from datetime import date
(date(year, month, day) - date(1, 1, 1)).days + 1
```

## `from_abs_days(days)`

Calculate the date `days` days since `0001/01/01`.

__Examples__
```python
import datetime
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=-1)
tomorrow = today + datetime.timedelta(days=1)

iroiro_today = (today.year, today.month, today.day)
iroiro_abs_days = to_abs_days(iroiro_today[0], iroiro_today[1], iroiro_today[2])

iroiro_tomorrow = from_abs_days(iroiro_abs_days + 1)
assert iroiro_tomorrow == (tomorrow.year, tomorrow.month, tomorrow.day)

iroiro_yesterday = from_abs_days(iroiro_abs_days + 1)
assert iroiro_yesterday == (yesterday.year, yesterday.month, yesterday.day)
```
