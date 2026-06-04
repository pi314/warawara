# iroiro.tui

This document describes the API set provided by `iroiro.tui`.

For the index of this package, see [iroiro.md](iroiro.md).


## Class `Lock`

A wrapper for standard `threading.Lock`.

Note that it's a wrapper, not a subclass, `isinstance()` won't trace back to standard `Lock`.

`Lock` objects support context management protocol (you can `with` it).


### `Lock.locked`

A integer value indicates how many times the lock is acquired.
*   For `Lock` it's either `0` or `1`
*   For `RLock` it's the acquired count

Access to this attribute is not guarded by locks, as it's already attached to a lock.


### `Lock.acquire(blocking=True, timeout=-1)`

Acquire the lock, and return a context manager that proxies `__getattr__()` to the lock object.

The returned object has `__bool__()` indicates whether it is acquired.

This opens the ability to `with` it with specified `blocking` and `timeout`:

```python
lock = iroiro.Lock()
with lock.acquire(blocking=False) as locked:
    if not locked:
        return
    print('critical section')

    # lock.release() is called on __exit__() if it's acquired
```


### `Lock.release()`

Release the lock.


## Class `RLock`

All methods are same as [Lock](#class-lock).

`locked()` method is added into standard library since Python 3.14.
Before that, iroiro backs you.


## Class `Timer`

A wrapper for standard `threading.Timer` that is reusable.

__Parameters__
```python
Timer(func, interval=None, *, args=None, kwargs=None)
```

`interval`, `args`, and `kwargs` could be specified as default values.

`args` should be in `list` or `tuple`.

`kwargs` should be in `dict`.

### `Timer.remaining`

The remaining time of the timer in seconds.

### `Timer.start()`

Start the timer.

__Parameters__
```
Timer.start(interval=None, *, args=None, kwargs=None):
```

`internal`, `args`, and `kwargs` overrides the default values.

### `Timer.cancel()`

Cancel the timer.

### `Timer.join()`

Join the timer.

### `Timer.active`

Indicates if the timer is running.

### `Timer.expired`

Indicates if the timer is expired.

### `Timer.idle`

Indicates if the timer is idle (before first start.)

### `Timer.cancel`

Indicates if the timer is canceled.
