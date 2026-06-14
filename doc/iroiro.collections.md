# iroiro.collections

This document describes the API set provided by `iroiro.collections`.

For the index of this package, see [iroiro.md](iroiro.md).


## Class `namablelist`

A list inspired by `namedtuple` that supports assiciating names with index.

__Parameters__
```python
namablelist(iterable)
namablelist(**kwargs)
```

__Examples__
```python
nl = namablelist([10, 11, 12, 13])
assert nl == [10, 11, 12, 13]

nl = namablelist(apple=10, banana=11, canana=12, danana=13)
assert nl == [10, 11, 12, 13]
```

In the `iterable` form, `namablelist` is created without any name bindings.

In the `**kwargs` form, `namablelist` is created with full name bindings.

Name bindings could be added/changed/deleted dynamically.


### Methods and Properties

#### `namablelist.nameit(index, name)`
Associate `index` with `name`.

__Examples__
```python
nl = namablelist([10, 11, 12, 13])
assert nl == [10, 11, 12, 13]

nl.nameit(0, 'apple')
nl.nameit(1, 'banana')
nl.nameit(2, 'canana')
nl.nameit(3, 'danana')
assert nl.apple  == 10
assert nl.banana == 11
assert nl.canana == 12
assert nl.danana == 13
assert nl['apple']  == 10
assert nl['banana'] == 11
assert nl['canana'] == 12
assert nl['danana'] == 13
```

#### `namablelist.unname(arg)`
Unassociate `arg`. `arg` can either be an index or a name.

__Examples__
```python
nl = namablelist(apple=10, banana=11, canana=12, danana=13)
assert nl == [10, 11, 12, 13]
assert nl.apple  == 10
assert nl.banana == 11
assert nl.canana == 12
assert nl.danana == 13

nl.unname(0)
nl.apple    # AttributeError
nl['apple'] # KeyError

nl.unname('canana')
nl.canana    # AttributeError
nl['canana'] # KeyError
```
