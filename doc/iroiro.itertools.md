# iroiro.itertools

This document describes the API set provided by `iroiro.itertools`.

For the index of this package, see [iroiro.md](iroiro.md).


## `is_iterable(obj)`

Return `True` if `obj` is iterable and `False` otherwise.

__Examples__
```python
assert is_iterable([])
assert is_iterable("iroiro")
assert not is_iterable(3)
```


## `unwrap(obj=None)`

Try to unpack `obj` as much as possible.

`str` stays as-is and they don't unpack to characters.

__Examples__
```python
assert unwrap([[[1, 2, 3]]]) == [1, 2, 3]
assert unwrap([[True]]) == True
assert unwrap(3) == 3
assert unwrap('iroiro') == 'iroiro'
```


## `flatten(tree)`

Flatten every nested list/tuple and merge them into one.

__Examples__
```python
assert flatten([[1, 2, 3], [4, 5, 6], [7], [8, 9]]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
```


## `lookahead(iterable)`

Return a generator object that generate boolean values to indicate the last element.

Like `enumerate()` that generate `index` values for each element,
`lookahead()` generate `is_last`.

__Examples__
```python
assert list(lookahead([1, 2, 3, 4, 5])) == [
   (1, False),
   (2, False),
   (3, False),
   (4, False),
   (5, True),
   ]
```


## `zip_longest(*iterables, fillvalues=None)`

Similar to the standard `itertools.zip_longest()`, but iroiro version supports
setting `fillvalue` for each iterable.

If `fillvalues` is neither a `tuple` nor a `list`, the value is duplicated for each iterable.

__Examples__
```python
# Same as itertools.zip_longest()
A = list(zip_longest('ABCD', [1, 2], fillvalues='#')),
B = [
   ('A', 1),
   ('B', 2),
   ('C', '#'),
   ('D', '#'),
   ]
assert A == B

A = list(zip_longest('ABCD', [1, 2], fillvalues=('#', 0))),
B = [
   ('A', 1),
   ('B', 2),
   ('C', 0),
   ('D', 0),
   ]
assert A == B

A = list(zip_longest('AB', [1, 2, 3, 4], fillvalues=('#', 0))),
B = [
   ('A', 1),
   ('B', 2),
   ('#', 3),
   ('#', 4),
   ]
assert A == B
```

## `chaining()`

Return a helper object that allows method-chaining style operation.

```python
res = (chaining([1, 0, 1, 2, 3, 0, 5, 8, 13])
       .filter()
       .map(lambda x: x * 2)
       .enumerate()
       .starmap(lambda idx, elem: idx + elem)
       .reduce(lambda a, b: a + b))
assert res == 87
```

The helper object has the following methods that returns a new helper object
for further chaining:

*   `.map(func)`: same as `map(func, data)`
*   `.starmap(func)`: same as `starmap(func, data)`
*   `.filter(func=None)`: same as `filter(func, data)`
*   `.starfilter(func=None)`: like `filter()` but `star`
*   `.concat(*others)`: concatenate additional iterables to the helper object
    -   The added iterables are casted into the same type as the first one
*   `.enumerate(start=0)`: same as `enumerate(data, start)`
*   `.zip(*others, fill=None)`: same as `zip(data, *others)`
    -   Any iterables that are not long enough are filled with `fill`
*   `.zipleft(*others, fill=None)`: same as `zip(*others, data)`
*   `.sort(key=None)`: same as `sorted(data, key)`

All the methods above are lazy and the operations are implicitly stored with an iterator.  
Calling `.eval()` evaluates and returns the result.

These methods return the processed result directly,
as they naturally reduce a dimension from the input:
*   `.reduce(func, initial=)`: same as `functools.reduce(func, data, initial=)`
*   `.join(sep=' ')`: same as `sep.join(data)`
*   `.min(key=None)`: same as `min(data, key)`
*   `.max(key=None)`: same as `max(data, key)`

The following methods are for `dict`:

*   `.items()`: same as `dict.items()`
*   `.keys()`: same as `dict.keys()`
*   `.values()`: same as `dict.values()`

The following methods are provided for casting the result:

*   `.to_dict()`: `dict(data)`
*   `.to_list()`: `list(data)`
*   `.to_tuple()`: `tuple(data)`
*   `.to_set()`: `set(data)`
