#include "scribo.hpp"

#include "line_detector.hpp"

namespace pln::scribo
{
  void define_scribo(pybind11::module& _m)
  {
    auto m = _m.def_submodule("scribo");
    pln::scribo::def_line_detector(m);
  }
} // namespace pln::scribo