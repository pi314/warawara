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

#### `TestCase.eq()` / `TestCase.ne()`
An alias to `self.assertEqual` and `self.assertNotEqual`, respectively.

#### `TestCase.le()` / `TestCase.lt()`
An alias to `self.assertLessEqual` and `self.assertLess`, respectively.

#### `TestCase.ge()` / `TestCase.gt()`
An alias to `self.assertGreaterEqual` and `self.assertGreater`, respectively.

#### `TestCase.true()` / `TestCase.false()`
An alias to `self.assertTrue` and `self.assertFalse`, respectively.

#### `TestCase.raises()`
An alias to `self.assertRaises`.

#### `TestCase.checkpoint()`
Create a [Checkpoint](#class-checkpoint) object, see below.

#### `TestCase.run_in_thread(func, args=tuple(), kwargs=dict())`
Run `func(*args, **kwargs)` in a daemon thread.

The return value is a context manager.  
It `start()` the thread on `__enter__`, and `join()` the thread on `__exit__`.
The object is not reusable.

__Examples__
```python
import warawara
import threading

class TestRunInThread(TestCase):
    def test_run_in_thread(self):
        barrier = threading.Barrier(2)
        checkpoint = False

        def may_stuck():
            nonlocal checkpoint
            barrier.wait()
            checkpoint = True

        with self.run_in_thread(may_stuck):
            self.false(checkpoint)
            barrier.wait()

        self.true(checkpoint)
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

A wrapper to `threading.Event()` that links to a `Testcase`.

### Methods and Properties

#### `Checkpoint.set()` / `Checkpoint.clear()`
Set/Clear the checkpoint.

#### `Checkpoint.is_set()`
Return if the checkpoint was already set.

#### `Checkpoint.wait()`
Block the execution and wait for the checkpoint to be set.

#### `Checkpoint.check(is_set=True)`
Check if `checkpoint.is_set()` equals to argument `is_set`. If not, fail the testcase.

#### `Checkpoint.__bool__()`
Return `self.is_set()`.
