# iroiro.tui

This document describes the API set provided by `iroiro.tui`.

For the index of this package, see [iroiro.md](iroiro.md).


## Class `Lock`

A wrapper to standard `threading.Lock`.

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
