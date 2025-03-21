#include <stdexcept>

#include "se.hpp"

namespace pln::morpho
{
  namespace details
  {
    mask2d::mask2d(pybind11::array arr)
    {
      if (arr.ndim() != 2)
        throw std::invalid_argument("Mask2d must be a 2D array");
      int width = arr.shape(1);
      int height = arr.shape(0);
      if (width == 0 || width % 2 == 0)
        throw std::invalid_argument("Width should be odd and non zero");
      if (height == 0 || height % 2 == 0)
        throw std::invalid_argument("height should be odd and non zero");
      
      auto buf = arr.request();
      bool* buffer = static_cast<bool*>(buf.ptr);
      m_radial_extent = std::max(width, height) / 2;

      m_points.reserve(width * height);
      int i = 0;
      for (int y = -(height/2); y <= (height/2); ++y)
      {
        for (auto x = -(width/2); x <= (width/2); ++x)
        {
          if (*(buffer+i))
            m_points.push_back({x, y});
          i++;
        }
      }
    }

    ::ranges::span<const mln::point2d> mask2d::offsets() const
    {
      return ::ranges::make_span(m_points.data(), m_points.size());
    }

    mln::box2d mask2d::compute_input_region(mln::box2d roi) const
    {
      roi.inflate(radial_extent());
      return roi;
    }
    mln::box2d mask2d::compute_output_region(mln::box2d roi) const
    {
      roi.inflate(-radial_extent());
      return roi;
    }
  }

  structuring_element_2d::structuring_element_2d(float radius)
    : m_se(std::in_place_type<mln::se::disc>, radius)
    , m_kind(kind::DISC)
  {
  }

  structuring_element_2d::structuring_element_2d(int width, int height)
    : m_se(std::in_place_type<mln::se::rect2d>, width, height)
    , m_kind(kind::RECT)
  {
  }

  structuring_element_2d::structuring_element_2d(pybind11::tuple period, int k)
    : m_se(std::in_place_type<mln::se::periodic_line2d>,
           mln::point2d{pybind11::cast<int>(period[0]), pybind11::cast<int>(period[1])}, k)
    , m_kind(kind::PERIODIC_LINE)
  {
  }

  structuring_element_2d::structuring_element_2d(pybind11::array arr)
    : m_se(std::in_place_type<details::mask2d>, arr)
    , m_kind(kind::MASK)
  {
  }

  structuring_element_2d::kind structuring_element_2d::type() const { return m_kind; }

  const mln::se::disc& structuring_element_2d::as_disc() const
  {
    assert(m_kind == kind::DISC);
    return std::get<mln::se::disc>(m_se);
  }

  const mln::se::rect2d& structuring_element_2d::as_rect() const
  {
    assert(m_kind == kind::RECT);
    return std::get<mln::se::rect2d>(m_se);
  }

  const mln::se::periodic_line2d& structuring_element_2d::as_periodic_line() const
  {
    assert(m_kind == kind::PERIODIC_LINE);
    return std::get<mln::se::periodic_line2d>(m_se);
  }

  const details::mask2d& structuring_element_2d::as_mask() const
  {
    assert(m_kind == kind::MASK);
    return std::get<details::mask2d>(m_se);
  }

  void def_se(pybind11::module& m)
  {
    auto se_class = pybind11::class_<structuring_element_2d>(m, "structuring_element_2d")
                        .def(pybind11::init<float>())
                        .def(pybind11::init<int, int>())
                        .def(pybind11::init<pybind11::tuple, int>())
                        .def(pybind11::init<pybind11::array>())
                        .def("type", &structuring_element_2d::type)
                        .def("as_disc", &structuring_element_2d::as_disc)
                        .def("as_rect", &structuring_element_2d::as_rect)
                        .def("as_periodic_line", &structuring_element_2d::as_periodic_line)
                        .def("as_mask", &structuring_element_2d::as_mask);

    pybind11::enum_<structuring_element_2d::kind>(se_class, "kind")
        .value("DISC", structuring_element_2d::kind::DISC)
        .value("RECT", structuring_element_2d::kind::RECT)
        .value("PERIODIC_LINE", structuring_element_2d::kind::PERIODIC_LINE)
        .value("MASK", structuring_element_2d::kind::MASK);
  }
} // namespace pln::morpho