#pragma once

#include <mln/core/se/disc.hpp>
#include <mln/core/se/periodic_line2d.hpp>
#include <mln/core/se/private/se_facade.hpp>
#include <mln/core/se/rect2d.hpp>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <variant>

namespace pln::morpho
{
  namespace details
  {
    class mask2d : public mln::se_facade<mask2d>
    {
    public:
      using category     = mln::dynamic_neighborhood_tag;
      using separable    = std::false_type;
      using decomposable = std::false_type;
      using incremental  = std::false_type;

      mask2d(pybind11::array);

      [[gnu::pure]] ::ranges::span<const mln::point2d> offsets() const;

      int radial_extent() const { return m_radial_extent; };

      mln::box2d compute_input_region(mln::box2d) const;
      mln::box2d compute_output_region(mln::box2d) const;

    private:
      std::vector<mln::point2d> m_points;
      int                       m_radial_extent;
    };
  } // namespace details

  class structuring_element_2d
  {
  public:
    enum class kind
    {
      RECT,
      DISC,
      PERIODIC_LINE,
      MASK
    };

  public:
    structuring_element_2d(float);
    structuring_element_2d(int, int);
    structuring_element_2d(pybind11::tuple, int);
    structuring_element_2d(pybind11::array);

    const mln::se::disc&            as_disc() const;
    const mln::se::rect2d&          as_rect() const;
    const mln::se::periodic_line2d& as_periodic_line() const;
    const details::mask2d&          as_mask() const;

    template <typename SE>
    const SE& as() const
    {
      return std::get<SE>(m_se);
    }

    kind type() const;

    auto& get_variant() { return m_se; }
    const auto& get_variant() const { return m_se; }

  private:
    std::variant<mln::se::disc, mln::se::rect2d, mln::se::periodic_line2d, details::mask2d> m_se;
    kind                                                                                    m_kind;
  };

  template <typename SE>
  struct se2d_static_to_dyn;

  template <>
  struct se2d_static_to_dyn<mln::se::disc>
  {
    static constexpr auto kind = structuring_element_2d::kind::DISC;
  };

  template <>
  struct se2d_static_to_dyn<mln::se::rect2d>
  {
    static constexpr auto kind = structuring_element_2d::kind::RECT;
  };

  template <>
  struct se2d_static_to_dyn<mln::se::periodic_line2d>
  {
    static constexpr auto kind = structuring_element_2d::kind::PERIODIC_LINE;
  };

  template <>
  struct se2d_static_to_dyn<details::mask2d>
  {
    static constexpr auto kind = structuring_element_2d::kind::MASK;
  };

  void def_se(pybind11::module&);
} // namespace pln::morpho