#pragma once

#include <pybind11/pybind11.h>

namespace pln::morpho
{
  void def_maxtree(pybind11::module& m);
} // namespace pln::morpho