#pragma once

#include <pybind11/pybind11.h>

namespace pln::scribo
{
  void def_line_detector(pybind11::module& m);
} // namespace pln::scribo