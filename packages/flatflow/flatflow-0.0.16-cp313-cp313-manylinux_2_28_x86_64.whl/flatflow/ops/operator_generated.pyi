from __future__ import annotations

import flatbuffers
import numpy as np

import flatbuffers
import typing

uoffset: typing.TypeAlias = flatbuffers.number_types.UOffsetTFlags.py_type

class Operator(object):
  _SOFTMAX: int
  _TO_COPY: int
  _UNSAFE_VIEW: int
  ADD_TENSOR: int
  ARANGE: int
  ARANGE_START: int
  BMM: int
  CAT: int
  CLONE: int
  COS: int
  EMBEDDING: int
  EXPAND: int
  FULL: int
  GT_TENSOR: int
  MEAN_DIM: int
  MM: int
  MUL_SCALAR: int
  MUL_TENSOR: int
  NEG: int
  POW_TENSOR_SCALAR: int
  RSQRT: int
  SILU: int
  SIN: int
  SLICE_TENSOR: int
  T: int
  TRANSPOSE_INT: int
  TRIU: int
  UNSQUEEZE: int
  VIEW: int

