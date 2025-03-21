#pragma once

#include <mln/core/image/ndbuffer_image.hpp>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <fmt/format.h>

namespace pln
{
  /// \brief Convert a NumPy array to a ndbuffer_image
  /// \param[in] arr A NumPy array
  /// \return A ndbuffer_image
  PYBIND11_EXPORT mln::ndbuffer_image from_numpy(pybind11::array arr);

  /// \brief Convert a ndbuffer_image array to a NumPy
  /// \param[in] arr A ndbuffer_image
  /// \return A NumPy array
  PYBIND11_EXPORT pybind11::object to_numpy(const mln::ndbuffer_image& img);


  /// \brief Export the binding of the class
  /// ndbuffer_image_data
  /// \param[in] m The module in which the class will be exported
  PYBIND11_EXPORT void init_pylena_numpy(pybind11::module& m);
} // namespace pln

namespace pybind11::detail
{
  template <>
  struct type_caster<mln::ndbuffer_image>
  {
    PYBIND11_TYPE_CASTER(mln::ndbuffer_image, const_name("numpy.ndarray"));

    bool load(handle h, bool)
    {
      if (!pybind11::array::check_(h)) {
        auto msg = fmt::format("Input value is not a valid array (Got `{}`)", static_cast<std::string>(pybind11::str(pybind11::type::handle_of(h))));
        throw std::invalid_argument(msg);
      }
      pybind11::array arr = reinterpret_borrow<pybind11::array>(h);
      value               = pln::from_numpy(arr);
      return true;
    }

    static handle cast(const mln::ndbuffer_image& img, return_value_policy, handle) { return pln::to_numpy(img).inc_ref(); }
  };
} // namespace pybind11::detail