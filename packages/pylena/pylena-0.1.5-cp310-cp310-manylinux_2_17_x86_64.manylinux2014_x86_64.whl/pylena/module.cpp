#include <pln/image_cast.hpp>

#include <pybind11/pybind11.h>

#include "morpho/morpho.hpp"
#include "scribo/scribo.hpp"

namespace pln
{
  PYBIND11_MODULE(pylena_cxx, m)
  {
    pln::init_pylena_numpy(m);
    pln::morpho::define_morpho(m);
    pln::scribo::define_scribo(m);
  }
} // namespace pln