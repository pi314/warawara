# iroiro.fs

This document describes the API set provided by `iroiro.fs`.

For the index of this package, see [iroiro.md](iroiro.md).

## `getter()`
Equals to `property()`. See [setter()](#setter) for why this exists.


## `setter()`
A replacement to `@xxx.setter`.

Python's setter has an assumption:
the decorated function name should be the same as its property.

```python
class Foo:
    @property
    def bar(self):
        ...

    @bar.setter
    def barbar(self):
        ''' This function has no effect '''

foo = Foo()
foo.bar = 42 # AttributeError: property 'bar' of 'Foo' object has no setter
```

But it doesn't have to be. And that causes an unintuitive effect:

```python
class Foo:
    @property
    def bar(self):
        ...

    @bar.setter
    def barbar(self, value):
        print('This function is called')

foo = Foo()
foo.barbar = 42 # works
```

What makes thing even worse is that Python doesn't check if a method with the
same name is defined twice:

```python
class Foo:
    @property
    def bar(self):
        ...

    @bar.setter
    def barbar(self, value):
        print('This function is shadowed')

    def barbar(self, value):
        print('This function is also shadowed')

foo = Foo()
foo.barbar = 42 # silent
```

With `getter()` and `setter()`, this problem is removed:

```python
class Foo:
    @getter
    def bar(self):
        ...

    @setter
    def bar(self, value):
        print(f'bar = {value}')

foo = Foo()
foo.bar = 42
```
