# warawara.test_utils

This document describes the API set provided by `warawara.test_utils`.

For the index of this package, see [warawara.md](warawara.md).


## class `TestCase`

A sub-class of `unittest.TestCase` with a few extensions.

### Parameters
```python
TestCase(*args, **kwargs)
```

### Methods and Properties

#### `TestCase.eq()`
An alias to `self.assertEqual`.

#### `TestCase.ne()`
An alias to `self.assertNotEqual`.

#### `TestCase.le()`
An alias to `self.assertLessEqual`.

#### `TestCase.lt()`
An alias to `self.assertLess`.

#### `TestCase.ge()`
An alias to `self.assertGreaterEqual`.

#### `TestCase.gt()`
An alias to `self.assertGreater`.

#### `TestCase.true()`
An alias to `self.assertTrue`.

#### `TestCase.false()`
An alias to `self.assertFalse`.

#### `TestCase.raises()`
An alias to `self.assertRaises`.

#### `TestCase.checkpoint()`
Creates a `Checkpoint` object.

#### `TestCase.run_in_thread(func, args=tuple(), kwargs=dict())`
Run `func(*args, **kwargs)` in a daemon thread.

The return value is a context manager.  
It `start()` the thread on `__enter__`, and `join()` the thread on `__exit__`.

__Examples__
```python
def may_stuck():
    ...
    checkpoint.set()

with self.run_in_thread(may_stuck):
    checkpoint.check()
```

#### `TestCase.patch(name, side_effect)`

Patch out `name` with `side_effect`.

The patch is automatically cleaned up after each test case run.

__Examples__
```python
self.patch('builtins.open', mock_open)
```
After the aboved `patch()` call, any calls to `open()` will be forwared to `mock_open`.


## class `Checkpoint`

A wrapper to `threading.Event()` that binds with a `Testcase`.

### Parameters
```python
Checkpoint(testcase)
```

### Methods and Properties

#### `Checkpoint.set()`
Set the checkpoint.

#### `Checkpoint.unset()`
Unset the checkpoint.

#### `Checkpoint.wait()`
Block the execution and wait for the checkpoint to be set.

#### `Checkpoint.is_set()`
Return if the checkpoint was already set.

#### `Checkpoint.check()`
Check if the checkpoint was already set. If not, fail with the testcase.

#### `Checkpoint.check_not()`
Check if the checkpoint was already set. If yes, fail with the testcase.

#### `Checkpoint.__bool__()`
An alias to `self.is_set()`
