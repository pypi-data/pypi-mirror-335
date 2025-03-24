# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2009 Gael Varoquaux
# License: BSD Style, 3 clauses.

import pickle
import hashlib
import sys
import types
import io
import decimal

try:
  import numpy
except:
  has_numpy = False
else:
  has_numpy = True

Pickler = pickle._Pickler


class _ConsistentSet(object):
  def __init__(self, set_sequence):
    try:
      self._sequence = sorted(set_sequence)
    except (TypeError, decimal.InvalidOperation):
      self._sequence = sorted(map(hash_obj, set_sequence))


class _MyHash(object):
  """ Class used to hash objects that won't normally pickle """

  def __init__(self, *args):
    self.args = args


class Hasher(Pickler):
  """ A subclass of pickler, to do cryptographic hashing, rather than pickling. """

  def __init__(self, hash_name="md5"):
    self.stream = io.BytesIO()
    # We want a pickle protocol that only changes with major Python versions
    protocol = pickle.HIGHEST_PROTOCOL
    Pickler.__init__(self, self.stream, protocol=protocol)
    self._hash = hashlib.new(hash_name)

  def hash(self, obj) -> str:
    try:
      self.dump(obj)
    except pickle.PicklingError as e:
      e.args += ("PicklingError while hashing %r: %r" % (obj, e),)
      raise
    dumps = self.stream.getvalue()
    self._hash.update(dumps)
    return self._hash.hexdigest()

  def save(self, obj):
    if isinstance(obj, (types.MethodType, type({}.pop))):
      # the Pickler cannot pickle instance methods; here we decompose
      # them into components that make them uniquely identifiable
      if hasattr(obj, "__func__"):
        func_name = obj.__func__.__name__
      else:
        func_name = obj.__name__
      inst = obj.__self__
      if type(inst) == type(pickle):
        obj = _MyHash(func_name, inst.__name__)
      elif inst is None:
        # type(None) or type(module) do not pickle
        obj = _MyHash(func_name, inst)
      else:
        cls = obj.__self__.__class__
        obj = _MyHash(func_name, inst, cls)
    Pickler.save(self, obj)

  def memoize(self, obj):
    # We want hashing to be sensitive to value instead of reference.
    # For example we want ["aa", "aa"] and ["aa", "aaZ"[:2]]
    # to hash to the same value and that's why we disable memoization
    # for strings
    if isinstance(obj, (bytes, str)):
      return
    Pickler.memoize(self, obj)

  # The dispatch table of the pickler is not accessible in Python
  # 3, as these lines are only bugware for IPython, we skip them.
  def save_global(self, obj, name=None):
    # We have to override this method in order to deal with objects
    # defined interactively in IPython that are not injected in
    # __main__
    try:
      Pickler.save_global(self, obj, name=name)
    except pickle.PicklingError:
      Pickler.save_global(self, obj, name=name)
      module = getattr(obj, "__module__", None)
      if module == "__main__":
        my_name = name
        if my_name is None:
          my_name = obj.__name__
        mod = sys.modules[module]
        if not hasattr(mod, my_name):
          # IPython doesn't inject the variables define
          # interactively in __main__
          setattr(mod, my_name, obj)

  def _batch_setitems(self, items):
    try:
      Pickler._batch_setitems(self, iter(sorted(items)))
    except TypeError:
      Pickler._batch_setitems(self, iter(sorted((hash_obj(k), v) for k, v in items)))

  def save_set(self, set_items):
    Pickler.save(self, _ConsistentSet(set_items))

  dispatch = Pickler.dispatch.copy()
  dispatch[type(len)] = save_global # builtin
  dispatch[type(object)] = save_global # type
  dispatch[type(Pickler)] = save_global # classobj
  dispatch[type(pickle.dump)] = save_global # function
  dispatch[type(set())] = save_set


class NumpyHasher(Hasher):
  def __init__(self, hash_name="md5"):
    Hasher.__init__(self, hash_name=hash_name)

  def save(self, obj):
    """ Subclass the save method, to hash ndarray subclass, rather
      than pickling them. Off course, this is a total abuse of
      the Pickler class.
    """
    import numpy as np

    if isinstance(obj, np.ndarray) and not obj.dtype.hasobject:
      # Compute a hash of the object
      # The update function of the hash requires a c_contiguous buffer.
      if obj.shape == ():
        # 0d arrays need to be flattened because viewing them as bytes
        # raises a ValueError exception.
        obj_c_contiguous = obj.flatten()
      elif obj.flags.c_contiguous:
        obj_c_contiguous = obj
      elif obj.flags.f_contiguous:
        obj_c_contiguous = obj.T
      else:
        # Cater for non-single-segment arrays: this creates a
        # copy, and thus aleviates this issue.
        # XXX: There might be a more efficient way of doing this
        obj_c_contiguous = obj.flatten()

      # View the array as bytes to support dtypes like datetime64
      self._hash.update(memoryview(obj_c_contiguous.view(np.uint8)))

      # The object will be pickled by the pickler hashed at the end.
      obj = (obj.__class__, ("HASHED", obj.dtype, obj.shape, obj.strides))
    elif isinstance(obj, np.dtype):
      # Atomic dtype objects are interned by their default constructor:
      # np.dtype("f8") is np.dtype("f8")
      # This interning is not maintained by a
      # pickle.loads + pickle.dumps cycle, because __reduce__
      # uses copy=True in the dtype constructor. This
      # non-deterministic behavior causes the internal memoizer
      # of the hasher to generate different hash values
      # depending on the history of the dtype object.
      # To prevent the hash from being sensitive to this, we use
      # .descr which is a full (and never interned) description of
      # the array dtype according to the numpy doc.
      obj = (obj.__class__, ("HASHED", obj.descr))

    Hasher.save(self, obj)


def hash_obj(obj, hash_name="md5") -> str:
  if has_numpy:
    return NumpyHasher(hash_name=hash_name).hash(obj)
  else:
    return Hasher(hash_name=hash_name).hash(obj)

hash = hash_obj
