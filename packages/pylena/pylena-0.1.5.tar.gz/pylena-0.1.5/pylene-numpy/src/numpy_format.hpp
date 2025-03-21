#pragma once

#include <mln/core/image_format.hpp>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace pln
{
  /// \brief Conversion from enumerated type to NumPy string type
  /// \param[in] type An enumerated type
  /// \return A dtype corresponding to the NumPy type
  pybind11::dtype get_sample_type(mln::sample_type_id type);

  /// \brief Conversion from NumPy string type to enumerated type
  /// \param[in] type_format A string corresponding to the NumPy type
  /// \return An enumerated type
  mln::sample_type_id get_sample_type(const std::string& type_format);
} // namespace pln