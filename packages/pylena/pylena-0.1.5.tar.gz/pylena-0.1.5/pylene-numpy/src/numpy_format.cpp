#include "numpy_format.hpp"

namespace pln
{
  namespace details
  {
    template <mln::sample_type_id T>
    static pybind11::dtype dtype_of()
    {
      return pybind11::dtype::of<typename mln::sample_type_id_traits<T>::type>();
    }
  } // namespace details

  pybind11::dtype get_sample_type(mln::sample_type_id type)
  {
    switch (type)
    {
    case mln::sample_type_id::INT8:
      return details::dtype_of<mln::sample_type_id::INT8>();
    case mln::sample_type_id::INT16:
      return details::dtype_of<mln::sample_type_id::INT16>();
    case mln::sample_type_id::INT32:
      return details::dtype_of<mln::sample_type_id::INT32>();
    case mln::sample_type_id::INT64:
      return details::dtype_of<mln::sample_type_id::INT64>();
    case mln::sample_type_id::UINT8:
      return details::dtype_of<mln::sample_type_id::UINT8>();
    case mln::sample_type_id::UINT16:
      return details::dtype_of<mln::sample_type_id::UINT16>();
    case mln::sample_type_id::UINT32:
      return details::dtype_of<mln::sample_type_id::UINT32>();
    case mln::sample_type_id::UINT64:
      return details::dtype_of<mln::sample_type_id::UINT64>();
    case mln::sample_type_id::FLOAT:
      return details::dtype_of<mln::sample_type_id::FLOAT>();
    case mln::sample_type_id::DOUBLE:
      return details::dtype_of<mln::sample_type_id::DOUBLE>();
    case mln::sample_type_id::BOOL:
      return details::dtype_of<mln::sample_type_id::BOOL>();
    case mln::sample_type_id::RGB8:
      return details::dtype_of<mln::sample_type_id::UINT8>();
    default:
      throw std::runtime_error("Invalid sample_type_id");
    }
    return pybind11::none();
  }

  mln::sample_type_id get_sample_type(const std::string& type_format)
  {
    pybind11::dtype type;
    try
    {
      type = pybind11::dtype(type_format);
    }
    catch (const std::exception&)
    {
      return mln::sample_type_id::OTHER;
    }
    if (type.is(details::dtype_of<mln::sample_type_id::INT8>()))
      return mln::sample_type_id::INT8;
    else if (type.is(details::dtype_of<mln::sample_type_id::INT16>()))
      return mln::sample_type_id::INT16;
    else if (type.is(details::dtype_of<mln::sample_type_id::INT32>()))
      return mln::sample_type_id::INT32;
    else if (type.is(details::dtype_of<mln::sample_type_id::INT64>()))
      return mln::sample_type_id::INT64;
    else if (type.is(details::dtype_of<mln::sample_type_id::UINT8>()))
      return mln::sample_type_id::UINT8;
    else if (type.is(details::dtype_of<mln::sample_type_id::UINT16>()))
      return mln::sample_type_id::UINT16;
    else if (type.is(details::dtype_of<mln::sample_type_id::UINT32>()))
      return mln::sample_type_id::UINT32;
    else if (type.is(details::dtype_of<mln::sample_type_id::UINT64>()))
      return mln::sample_type_id::UINT64;
    else if (type.is(details::dtype_of<mln::sample_type_id::FLOAT>()))
      return mln::sample_type_id::FLOAT;
    else if (type.is(details::dtype_of<mln::sample_type_id::DOUBLE>()))
      return mln::sample_type_id::DOUBLE;
    else if (type.is(details::dtype_of<mln::sample_type_id::BOOL>()))
      return mln::sample_type_id::BOOL;
    return mln::sample_type_id::OTHER;
  }
} // namespace pln