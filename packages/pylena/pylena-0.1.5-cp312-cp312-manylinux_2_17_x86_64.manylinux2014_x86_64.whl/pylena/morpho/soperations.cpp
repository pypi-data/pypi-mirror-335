#include <pln/image_cast.hpp>

#include <mln/core/image/ndimage.hpp>
#include <mln/morpho/closing.hpp>
#include <mln/morpho/dilation.hpp>
#include <mln/morpho/gradient.hpp>
#include <mln/morpho/opening.hpp>
#include <mln/core/extension/border_management.hpp>

#include "soperations.hpp"
#include <pybind11/stl.h>

namespace
{
  struct erosion_t
  {
    template <typename SE>
    mln::image2d<std::uint8_t> operator()(mln::image2d<std::uint8_t> img, const SE& se, std::optional<int> padding_value)
    {
      if (padding_value)
        return mln::morpho::erosion(img, se, mln::extension::bm::fill(static_cast<uint8_t>(padding_value.value())));
      else
        return mln::morpho::erosion(img, se);
    }
  };

  struct dilation_t
  {
    template <typename SE>
    mln::image2d<std::uint8_t> operator()(mln::image2d<std::uint8_t> img, const SE& se, std::optional<int> padding_value)
    {
      if (padding_value)
        return mln::morpho::dilation(img, se, mln::extension::bm::fill(static_cast<uint8_t>(padding_value.value())));
      else
        return mln::morpho::dilation(img, se);
    }
  };

  struct opening_t
  {
    template <typename SE>
    mln::image2d<std::uint8_t> operator()(mln::image2d<std::uint8_t> img, const SE& se, std::optional<int> padding_value)
    {
      if (padding_value)
        return mln::morpho::opening(img, se, mln::extension::bm::fill(static_cast<uint8_t>(padding_value.value())));
      else
        return mln::morpho::opening(img, se);
    }
  };

  struct closing_t
  {
    template <typename SE>
    mln::image2d<std::uint8_t> operator()(mln::image2d<std::uint8_t> img, const SE& se, std::optional<int> padding_value)
    {
      if (padding_value)
        return mln::morpho::closing(img, se, mln::extension::bm::fill(static_cast<uint8_t>(padding_value.value())));
      else
        return mln::morpho::closing(img, se);
    }
  };

  struct gradient_t
  {
    template <typename SE>
    mln::image2d<std::uint8_t> operator()(mln::image2d<std::uint8_t> img, const SE& se, std::optional<int> padding_value)
    {
      if (padding_value)
        throw std::runtime_error("Not implemented error. Padding value is not yet supported for gradient op.");
      else
        return mln::morpho::gradient(img, se);
    }
  };
} // namespace

namespace pln::morpho
{
  namespace details
  {
    template <class F>
    mln::ndbuffer_image morphological_operation_2d(mln::ndbuffer_image img, const structuring_element_2d& se, std::optional<int> padding_value)
    {
      se.get_variant();
      mln::image2d<std::uint8_t> ima = *(img.cast_to<std::uint8_t, 2>());
      auto op = [&ima,padding_value](const auto& se) -> mln::image2d<std::uint8_t> { return F()(ima, se, padding_value); };  
      return std::visit(op, se.get_variant());
    }
  } // namespace details

  void def_operations(pybind11::module& m)
  {
    m.def("erosion", &details::morphological_operation_2d<erosion_t>);
    m.def("dilation", &details::morphological_operation_2d<dilation_t>);
    m.def("opening", &details::morphological_operation_2d<opening_t>);
    m.def("closing", &details::morphological_operation_2d<closing_t>);
    m.def("gradient", &details::morphological_operation_2d<gradient_t>);
  }
} // namespace pln::morpho