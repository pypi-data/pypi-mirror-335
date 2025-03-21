#include <mln/core/image/private/ndbuffer_image_data.hpp>
#include <pln/image_cast.hpp>
#include "numpy_format.hpp"

#include <pybind11/cast.h>

#include <fmt/format.h>

#include <cassert>
#include <vector>

namespace pln
{
  mln::ndbuffer_image from_numpy(pybind11::array arr)
  {
    if (!pybind11::detail::check_flags(arr.ptr(), pybind11::detail::npy_api::NPY_ARRAY_C_CONTIGUOUS_))
      throw std::invalid_argument("Array should be C contiguous");
    auto                base = arr.base();
    const auto          info = arr.request();
    mln::sample_type_id type = get_sample_type(info.format);
    if (type == mln::sample_type_id::OTHER)
      throw std::invalid_argument(fmt::format(
          "Invalid dtype argument (Got dtype format {} expected types: [u]int[8, 16, 32, 64], float, double or bool)",
          info.format));
    const bool is_rgb8 = info.ndim == 3 && info.shape[2] == 3 && type == mln::sample_type_id::UINT8;
    const auto pdim    = info.ndim - (is_rgb8 ? 1 : 0);
    if (pdim > mln::PYLENE_NDBUFFER_DEFAULT_DIM)
      throw std::invalid_argument(
          fmt::format("Invalid number of dimension from numpy array (Got {} but should be less than {})", pdim,
                      mln::PYLENE_NDBUFFER_DEFAULT_DIM));
    int            size[mln::PYLENE_NDBUFFER_DEFAULT_DIM]    = {0};
    std::ptrdiff_t strides[mln::PYLENE_NDBUFFER_DEFAULT_DIM] = {0};
    for (auto d = 0; d < pdim; d++)
    {
      size[d]    = info.shape[pdim - d - 1];
      strides[d] = info.strides[pdim - d - 1];
    }
    const auto sample_type = is_rgb8 ? mln::sample_type_id::RGB8 : type;
    auto       res =
        mln::ndbuffer_image::from_buffer(reinterpret_cast<std::byte*>(info.ptr), sample_type, pdim, size, strides);
    if (base && pybind11::isinstance<mln::internal::ndbuffer_image_data>(base))
      res.__data() = pybind11::cast<std::shared_ptr<mln::internal::ndbuffer_image_data>>(base);
    return res;
  }

  pybind11::object to_numpy(const mln::ndbuffer_image& img)
  {
    const auto&      api   = pybind11::detail::npy_api::get();
    pybind11::object data  = pybind11::none();
    int              flags = pybind11::detail::npy_api::NPY_ARRAY_WRITEABLE_;
    if (img.__data())
    {
      data = pybind11::cast(img.__data());
      assert(data.ref_count() > 0);
    }

    /* For the moment, restrict RGB8 image to 2D image */
    const bool               is_rgb8 = img.pdim() == 2 && img.sample_type() == mln::sample_type_id::RGB8;
    const auto               ndim    = img.pdim() + (is_rgb8 ? 1 : 0);
    std::vector<std::size_t> strides(ndim, 1);
    std::vector<std::size_t> shapes(ndim, 3);
    auto                     descr = get_sample_type(img.sample_type());

    for (auto d = 0; d < img.pdim(); d++)
    {
      strides[d] = img.byte_stride(img.pdim() - d - 1);
      shapes[d]  = img.size(img.pdim() - d - 1);
    }

    auto res = pybind11::reinterpret_steal<pybind11::object>(api.PyArray_NewFromDescr_(
        api.PyArray_Type_, descr.release().ptr(), ndim, reinterpret_cast<Py_intptr_t*>(shapes.data()),
        reinterpret_cast<Py_intptr_t*>(strides.data()), reinterpret_cast<void*>(img.buffer()), flags, nullptr));

    if (!res)
      throw std::runtime_error("Unable to create the numpy array in ndimage -> array");
    if (data)
      // **Steal** a reference to data (https://numpy.org/devdocs/reference/c-api/array.html#c.PyArray_SetBaseObject)
      api.PyArray_SetBaseObject_(res.ptr(), data.release().ptr());
    return res;
  }

  void init_pylena_numpy(pybind11::module& m)
  {
    if (!pybind11::detail::get_global_type_info(typeid(mln::internal::ndbuffer_image_data)))
    {
      pybind11::class_<mln::internal::ndbuffer_image_data, std::shared_ptr<mln::internal::ndbuffer_image_data>>(
          m, "ndbuffer_image_data");
    }
  }
} // namespace pln