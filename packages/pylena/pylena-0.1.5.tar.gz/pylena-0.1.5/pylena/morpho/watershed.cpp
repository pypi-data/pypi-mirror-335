#include <mln/core/image/ndimage.hpp>
#include <mln/core/neighborhood/dyn_nbh_2d.hpp>
#include <mln/morpho/watershed.hpp>

#include <pln/image_cast.hpp>

#include <tuple>

#include "watershed.hpp"

namespace pln::morpho
{
  namespace details
  {
    std::pair<mln::ndbuffer_image, int> watershed(mln::ndbuffer_image _img, int connectivity, bool waterline)
    {
      mln::dyn_nbh_2d_t nbh(static_cast<mln::c2d_type>(connectivity));
      auto*             img = _img.cast_to<std::uint8_t, 2>();
      if (img)
      {
        int  nlabel;
        auto output = mln::morpho::watershed<std::int16_t>(*img, nbh, nlabel, waterline);
        return {std::move(output), nlabel};
      }
      else
        throw std::invalid_argument("Input image should be a 2D image with value encoded as uint8");
    }

    std::pair<mln::ndbuffer_image, int> watershed_from_markers(mln::ndbuffer_image _img, mln::ndbuffer_image _markers,
                                                               int connectivity)
    {
      mln::dyn_nbh_2d_t nbh(static_cast<mln::c2d_type>(connectivity));
      auto*             img = _img.cast_to<std::uint8_t, 2>();
      if (!img)
        throw std::invalid_argument("Input image should be a 2D image with value encoded as uint8");
      auto* markers = _markers.cast_to<std::int16_t, 2>();
      if (!markers)
        throw std::invalid_argument("Input markers should be a 2D image with value encoded as int16");
      int  nlabel;
      auto output = mln::morpho::watershed_from_markers<std::int16_t>(*img, nbh, *markers, nlabel);
      return {std::move(output), nlabel};
    }

  } // namespace details

  void def_watershed(pybind11::module_& m)
  {
    m.def("watershed", &details::watershed);
    m.def("watershed_from_markers", &details::watershed_from_markers);
  }
} // namespace pln::morpho