import re
from itertools import chain
from typing import Any, Callable, Iterable, overload

def noop() -> None:
  pass

def non_none[T](obj: T | None) -> T:
  assert obj is not None
  return obj

def as_any(obj: Any) -> Any:
  return obj

def list_split[T](l: list[T], sep: T) -> list[list[T]]:
  l = [sep, *l, sep]
  split_at = [i for i, x in enumerate(l) if x is sep]
  ranges = list(zip(split_at[0:-1], split_at[1:]))
  return [
    l[start + 1:end]
    for start, end in ranges
  ]

def drop_none[T](iterable: Iterable[T | None]) -> list[T]:
  return [x for x in iterable if x is not None]

def distinct[T](items: Iterable[T]) -> list[T]:
  return list(dict.fromkeys(items))

def first[T](iterable: Iterable[T]) -> T | None:
  return next(iter(iterable), None)

def move_value[T](iterable: Iterable[T], from_i: int, to_i: int) -> list[T]:
  l = list(iterable)
  l.insert(to_i, l.pop(from_i))
  return l

def transpose_dict(des):
  if isinstance(des, list):
    keys = list(des[0].keys()) if des else []
    length = len(des)
    return {
      key: [des[i][key] for i in range(length)]
      for key in keys
    }
  elif isinstance(des, dict):
    keys = list(des.keys())
    length = len(des[keys[0]]) if keys else 0
    return [
      {key: des[key][i] for key in keys}
      for i in range(length)
    ]
  raise ValueError("transpose_dict only accepts dict or list")

def make_combinations_by_dict(des, keys=None, pairs=[]):
  keys = sorted(des.keys()) if keys == None else keys
  if len(keys) == 0:
    return [dict(pairs)]
  key = keys[0]
  remaining_keys = keys[1:]
  new_pairs = [(key, val) for val in des[key]]
  return flatten([
    make_combinations_by_dict(des, remaining_keys, [pair] + pairs)
    for pair in new_pairs
  ])

def merge_dicts[T, K](*dicts: dict[K, T]) -> dict[K, T]:
  if len(dicts) == 1:
    return dicts[0]
  result = {}
  for d in dicts:
    result.update(d)
  return result

def intersect[T](*iterables: Iterable[T]) -> list[T]:
  return list(set.intersection(*map(set, iterables)))

def ensure_tuple[T](value: T | tuple[T, ...]) -> tuple[T, ...]:
  return value if isinstance(value, tuple) else (value,)

def key_of[T, U](dicts: Iterable[dict[T, U]], key: T) -> list[U]:
  return [d[key] for d in dicts]

def omit[T, K](d: dict[K, T], keys: Iterable[K]) -> dict[K, T]:
  if keys:
    d = dict(d)
    for key in keys:
      del d[key]
  return d

def pick[T, K](d: dict[K, T], keys: Iterable[K]) -> dict[K, T]:
  return {key: d[key] for key in keys}

def dict_by[T, K](keys: Iterable[K], values: Iterable[T]) -> dict[K, T]:
  return dict(zip(keys, values))

def tuple_by[T, K](d: dict[K, T], keys: Iterable[K]) -> tuple[T, ...]:
  return tuple(d[key] for key in keys)

def flatten[T](iterable: Iterable[Iterable[T]]) -> list[T]:
  return list(chain.from_iterable(iterable))

def transpose(tuples, default_num_returns=0):
  output = tuple(zip(*tuples))
  if not output:
    return ([],) * default_num_returns
  return tuple(map(list, output))

def map_dict[T, U, K](fn: Callable[[T], U], d: dict[K, T]) -> dict[K, U]:
  return {key: fn(value) for key, value in d.items()}

@overload
def deepen_dict[K1, U](d: dict[tuple[K1], U]) -> dict[K1, U]: ...
@overload
def deepen_dict[K1, K2, U](d: dict[tuple[K1, K2], U]) -> dict[K1, dict[K2, U]]: ...
@overload
def deepen_dict[K1, K2, K3, U](d: dict[tuple[K1, K2, K3], U]) -> dict[K1, dict[K2, dict[K3, U]]]: ...
@overload
def deepen_dict[K1, K2, K3, K4, U](d: dict[tuple[K1, K2, K3, K4], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, U]]]]: ...
@overload
def deepen_dict[K1, K2, K3, K4, K5, U](d: dict[tuple[K1, K2, K3, K4, K5], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, dict[K5, U]]]]]: ...
@overload
def deepen_dict[K1, K2, K3, K4, K5, K6, U](d: dict[tuple[K1, K2, K3, K4, K5, K6], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, dict[K5, dict[K6, U]]]]]]: ...
def deepen_dict(d: dict[tuple[Any, ...], Any]) -> dict:
  output = {}
  if () in d:
    return d[()]
  for (*tail, head), value in d.items():
    curr = output
    for key in tail:
      curr = curr.setdefault(key, {})
    curr[head] = value
  return output

def flatten_dict_inner(d, prefix=()):
  for key, value in d.items():
    if not isinstance(value, dict) or value == {}:
      yield prefix + (key,), value
    else:
      yield from flatten_dict_inner(value, prefix + (key,))

def flatten_dict(deep_dict: dict, prefix=()) -> dict:
  return dict(flatten_dict_inner(deep_dict, prefix))

def group[T, K](pairs: Iterable[tuple[K, T]]) -> dict[K, list[T]]:
  values_by_key = {}
  for key, value in pairs:
    values_by_key.setdefault(key, []).append(value)
  return values_by_key

def reversed_enumerate[T](l: list[T] | tuple[T, ...]) -> Iterable[tuple[int, T]]:
  return zip(reversed(range(len(l))), reversed(l))

def get_at[T](d: dict, keys: Iterable[Any], default: T) -> T:
  try:
    for key in keys:
      d = d[key]
  except KeyError:
    return default
  return as_any(d)

def for_each[T](func: Callable[[T], Any], iterable: Iterable[T]) -> None:
  for item in iterable:
    func(item)

def sized_partitions[T](values: Iterable[T], part_size: int) -> list[list[T]]:
  # "chunk"
  if not isinstance(values, list):
    values = list(values)
  num_parts = (len(values) / part_size).__ceil__()
  return [values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]

def num_partitions[T](values: Iterable[T], num_parts: int) -> list[list[T]]:
  if not isinstance(values, list):
    values = list(values)
  part_size = (len(values) / num_parts).__ceil__()
  return [values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]

def _cat_tile(cats, n_tile):
  import numpy as np
  return cats[np.tile(np.arange(len(cats)), n_tile)]

def df_from_array(
  value_cols: dict[str, Any],
  dim_labels: list[tuple[str, list[str | int | float]]],
  indexed=False,
):
  import numpy as np
  import pandas as pd
  dim_sizes = np.array([len(labels) for _, labels in dim_labels])
  assert all(array.shape == tuple(dim_sizes) for array in value_cols.values())
  array_offsets = [
    (dim_sizes[i + 1:].prod(), dim_sizes[:i].prod())
    for i in range(len(dim_sizes))
  ]
  category_cols = {
    dim: _cat_tile(pd.Categorical(labels).repeat(repeats), tiles)
    for (dim, labels), (repeats, tiles) in zip(dim_labels, array_offsets)
  }
  value_cols = {name: array.reshape(-1) for name, array in value_cols.items()}
  df = pd.DataFrame({**category_cols, **value_cols}, copy=False)
  if indexed:
    df = df.set_index([name for name, _ in dim_labels])
  return df

StrFilter = Callable[[str], bool]

def str_filterer(
  include_patterns: list[re.Pattern[str]] = [],
  exclude_patterns: list[re.Pattern[str]] = [],
) -> StrFilter:
  def str_filter(string: str) -> bool:
    if any(pattern.search(string) for pattern in exclude_patterns):
      return False
    if not include_patterns:
      return True
    return any(pattern.search(string) for pattern in include_patterns)

  return str_filter
