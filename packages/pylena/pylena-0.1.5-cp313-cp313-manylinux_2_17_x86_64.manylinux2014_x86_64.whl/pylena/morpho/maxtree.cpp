#include <mln/morpho/maxtree.hpp>

#include <mln/core/image/ndimage.hpp>
#include <mln/core/neighborhood/c26.hpp>
#include <mln/core/neighborhood/c4.hpp>
#include <mln/core/neighborhood/c6.hpp>
#include <mln/core/neighborhood/c8.hpp>
#include <mln/morpho/tos.hpp>
#include <pln/image_cast.hpp>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <iostream>

namespace py = pybind11;

namespace pln::morpho
{

  struct ComponentTree
  {
    py::array_t<uint8_t> get_values() const
    {
      py::array_t<uint8_t> r(_handle.values.size());
      std::copy(_handle.values.begin(), _handle.values.end(), r.mutable_data());
      return r;
    }

    py::array_t<int> get_parent() const
    {
      py::array_t<int> r(_handle.parent.size());
      std::copy(_handle.parent.begin(), _handle.parent.end(), r.mutable_data());
      return r;
    }

    mln::morpho::component_tree<uint8_t> _handle;
  };


  std::pair<ComponentTree, mln::ndbuffer_image> maxtreend(mln::ndbuffer_image input, int connectivity)
  {
    auto* in2 = input.cast_to<std::uint8_t, 2>();
    if (in2 != nullptr)
    {
      if (connectivity != 4 && connectivity != 8)
        throw std::invalid_argument("Connectivity should be 4 or 8");

      auto&& [maxtree, nodemap] =
          (connectivity == 4) ? mln::morpho::maxtree(*in2, mln::c4) : mln::morpho::maxtree(*in2, mln::c8);
      return {ComponentTree{std::move(maxtree)}, std::move(nodemap)};
    }

    auto* in3 = input.cast_to<std::uint8_t, 3>();
    if (in3 != nullptr)
    {
      if (connectivity != 6 && connectivity != 26)
        throw std::invalid_argument("Connectivity should be 6 or 26");

      auto&& [maxtree, nodemap] =
          (connectivity == 6) ? mln::morpho::maxtree(*in3, mln::c6) : mln::morpho::maxtree(*in3, mln::c26);
      return {ComponentTree{std::move(maxtree)}, std::move(nodemap)};
    }

    throw std::invalid_argument("Input image should be a 2D or 3D uint8 image");
  }

  std::pair<ComponentTree, mln::ndbuffer_image> tosnd(mln::ndbuffer_image input, py::object coordinate)
  {
    auto* in2 = input.cast_to<std::uint8_t, 2>();
    if (in2 != nullptr)
    {
      mln::point2d coord = in2->domain().tl();
      if (!coordinate.is_none())
      {
        auto c = py::cast<py::tuple>(coordinate);
        if (py::len(c) != 2)
          throw std::invalid_argument("The coordinate must be a pair of numbers");

        coord[0] = py::cast<int>(c[0]);
        coord[1] = py::cast<int>(c[1]);
      }

      auto&& [maxtree, nodemap] = mln::morpho::tos(*in2, coord);
      return {ComponentTree{std::move(maxtree)}, std::move(nodemap)};
    }

    auto* in3 = input.cast_to<std::uint8_t, 3>();
    if (in3 != nullptr)
    {
      mln::point3d coord = in3->domain().tl();
      if (!coordinate.is_none())
      {
        auto c = py::cast<py::tuple>(coordinate);
        if (py::len(c) != 3)
          throw std::invalid_argument("The coordinate must be a triple of numbers");

        coord[0] = py::cast<int>(c[0]);
        coord[1] = py::cast<int>(c[1]);
        coord[2] = py::cast<int>(c[2]);
      }

      auto&& [maxtree, nodemap] = mln::morpho::tos(*in3, coord);
      return {ComponentTree{std::move(maxtree)}, std::move(nodemap)};
    }

    throw std::invalid_argument("Input image should be a 2D or 3D uint8 image");
  }

  void def_maxtree(py::module_& m)
  {
    py::class_<pln::morpho::ComponentTree>(m, "ComponentTree")                    //
        .def(py::init<>())                                                        //
        .def_property_readonly("parent", &pln::morpho::ComponentTree::get_parent) //
        .def_property_readonly("values", &pln::morpho::ComponentTree::get_values);

    m.def("maxtree", &pln::morpho::maxtreend, "Compute the maxtree of a 2D or 3D image");
    m.def("tos", &pln::morpho::tosnd, py::arg("input"), py::arg("coordinate"),
          "Compute the Tree of Shapes of a 2D or 3D image");
  }
} // namespace pln::morpho