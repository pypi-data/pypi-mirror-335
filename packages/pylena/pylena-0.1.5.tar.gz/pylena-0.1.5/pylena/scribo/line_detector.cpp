#include "line_detector.hpp"

#include <mln/core/image/ndimage.hpp>
#include <scribo/segdet.hpp>

#include <pln/image_cast.hpp>
#include <pybind11/stl.h>

namespace pln::scribo
{
  namespace details
  {
    using namespace ::scribo;
    mln::image2d<std::uint8_t> get_img_2d_uint8(mln::ndbuffer_image _img)
    {
      auto* img = _img.cast_to<std::uint8_t, 2>();
      if (!img)
        throw std::invalid_argument("Input image should be a 2D image with value encoded as uint8");

      return *img;
    }

    void check_params(SegDetParams& params)
    {
      if (!params.is_valid())
        throw std::invalid_argument("Invalid SegDetParams");
    }

    std::vector<VSegment> line_detector_vector(mln::ndbuffer_image _img, int min_len, SegDetParams& params)
    {
      check_params(params);
      mln::image2d<std::uint8_t> img = get_img_2d_uint8(_img);

      auto output = detect_line_vector(img, min_len, params);

      return output;
    }

    std::tuple<mln::ndbuffer_image, std::vector<LSuperposition>> line_detector_pixel(mln::ndbuffer_image _img,
                                                                                     int min_len, SegDetParams& params)
    {
      check_params(params);
      mln::image2d<std::uint8_t> img = get_img_2d_uint8(_img);

      auto [out_img, superposition_map] = detect_line_label(img, min_len, params);
      mln::ndbuffer_image out_img_mln   = out_img;

      auto output = std::make_tuple(std::move(out_img_mln), std::move(superposition_map));
      return output;
    }

    std::tuple<mln::ndbuffer_image, std::vector<LSuperposition>, std::vector<VSegment>>
    line_detector_full(mln::ndbuffer_image _img, int min_len, SegDetParams& params)
    {
      check_params(params);
      mln::image2d<std::uint8_t> img = get_img_2d_uint8(_img);

      auto [out_img, superposition_map, segs_vector] = detect_line_full(img, min_len, params);
      mln::ndbuffer_image out_img_mln                = out_img;

      auto output = std::make_tuple(std::move(out_img_mln), std::move(superposition_map), std::move(segs_vector));
      return output;
    }
  } // namespace details

  void def_line_detector(pybind11::module& m)
  {
    using namespace ::scribo;

    pybind11::enum_<e_segdet_preprocess>(m, "e_segdet_preprocess")                                                    //
        .value("NONE", e_segdet_preprocess::NONE, "Do not perform any post processing before line detection")         //
        .value("BLACK_TOP_HAT", e_segdet_preprocess::BLACK_TOP_HAT,
               "Perform a black top hat as preprocessing to remove the background of the input image")                //
        .export_values();                                                                                             //

    pybind11::enum_<e_segdet_process_tracking>(m, "e_segdet_process_tracking")                                        //
        .value("KALMAN", e_segdet_process_tracking::KALMAN,
               "Kalman Filters following classics prediction and correction based on IRISA article")                  //
        .value("ONE_EURO", e_segdet_process_tracking::ONE_EURO,
               "One Euro Filter (modification from Nicolas Roussel code)")                                            //
        .value("DOUBLE_EXPONENTIAL", e_segdet_process_tracking::DOUBLE_EXPONENTIAL, "Double exponential filter")      //
        .value("LAST_INTEGRATION", e_segdet_process_tracking::LAST_INTEGRATION, "Last integration predictor")         //
        .value("SIMPLE_MOVING_AVERAGE", e_segdet_process_tracking::SIMPLE_MOVING_AVERAGE, "Simple moving average")    //
        .value("EXPONENTIAL_MOVING_AVERAGE", e_segdet_process_tracking::EXPONENTIAL_MOVING_AVERAGE,
               "Exponential moving average")                                                                          //
        .export_values();                                                                                             //

    pybind11::enum_<e_segdet_process_traversal_mode>(m, "e_segdet_process_traversal_mode")                            //
        .value("HORIZONTAL", e_segdet_process_traversal_mode::HORIZONTAL,
               "To perform the line detection only horizontaly")                                                      //
        .value("VERTICAL", e_segdet_process_traversal_mode::VERTICAL, "To perform the line detection only verticaly") //
        .value("HORIZONTAL_VERTICAL", e_segdet_process_traversal_mode::HORIZONTAL_VERTICAL,
               "To perform the line detection both horizontaly and verticaly")                                        //
        .export_values();                                                                                             //

    pybind11::enum_<e_segdet_process_extraction>(m, "e_segdet_process_extraction")                                    //
        .value("BINARY", e_segdet_process_extraction::BINARY, "Binary extraction with threshold")                     //
        .value("GRADIENT", e_segdet_process_extraction::GRADIENT, "Gradient extraction with threshold")               //
        .export_values();                                                                                             //

    pybind11::class_<SegDetParams>(m, "SegDetParams")                                                                 //
        .def(pybind11::init<>())                                                                                      //
        .def_readwrite("preprocess", &SegDetParams::preprocess)                                                       //
        .def_readwrite("tracker", &SegDetParams::tracker)                                                             //
        .def_readwrite("traversal_mode", &SegDetParams::traversal_mode)                                               //
        .def_readwrite("extraction_type", &SegDetParams::extraction_type)                                             //
        .def_readwrite("negate_image", &SegDetParams::negate_image)                                                   //
        .def_readwrite("dyn", &SegDetParams::dyn)                                                                     //
        .def_readwrite("size_mask", &SegDetParams::size_mask)                                                         //
        .def_readwrite("double_exponential_alpha", &SegDetParams::double_exponential_alpha)                           //
        .def_readwrite("simple_moving_average_memory", &SegDetParams::simple_moving_average_memory)                   //
        .def_readwrite("exponential_moving_average_memory", &SegDetParams::exponential_moving_average_memory)         //
        .def_readwrite("one_euro_beta", &SegDetParams::one_euro_beta)                                                 //
        .def_readwrite("one_euro_mincutoff", &SegDetParams::one_euro_mincutoff)                                       //
        .def_readwrite("one_euro_dcutoff", &SegDetParams::one_euro_dcutoff)                                           //
        .def_readwrite("bucket_size", &SegDetParams::bucket_size)                                                     //
        .def_readwrite("nb_values_to_keep", &SegDetParams::nb_values_to_keep)                                         //
        .def_readwrite("discontinuity_relative", &SegDetParams::discontinuity_relative)                               //
        .def_readwrite("discontinuity_absolute", &SegDetParams::discontinuity_absolute)                               //
        .def_readwrite("minimum_for_fusion", &SegDetParams::minimum_for_fusion)                                       //
        .def_readwrite("default_sigma_position", &SegDetParams::default_sigma_position)                               //
        .def_readwrite("default_sigma_thickness", &SegDetParams::default_sigma_thickness)                             //
        .def_readwrite("default_sigma_luminosity", &SegDetParams::default_sigma_luminosity)                           //
        .def_readwrite("min_nb_values_sigma", &SegDetParams::min_nb_values_sigma)                                     //
        .def_readwrite("sigma_pos_min", &SegDetParams::sigma_pos_min)                                                 //
        .def_readwrite("sigma_thickness_min", &SegDetParams::sigma_thickness_min)                                     //
        .def_readwrite("sigma_luminosity_min", &SegDetParams::sigma_luminosity_min)                                   //
        .def_readwrite("gradient_threshold", &SegDetParams::gradient_threshold)                                       //
        .def_readwrite("llumi", &SegDetParams::llumi)                                                                 //
        .def_readwrite("blumi", &SegDetParams::blumi)                                                                 //
        .def_readwrite("ratio_lum", &SegDetParams::ratio_lum)                                                         //
        .def_readwrite("max_thickness", &SegDetParams::max_thickness)                                                 //
        .def_readwrite("threshold_intersection", &SegDetParams::threshold_intersection)                               //
        .def_readwrite("remove_duplicates", &SegDetParams::remove_duplicates)                                         //
        .def("__repr__",
             [](const SegDetParams& a) {
               return "<scribo.SegDetParams: preprocess=" + std::to_string(static_cast<int>(a.preprocess)) +
                      ", tracker=" + std::to_string(static_cast<int>(a.tracker)) +
                      ", traversal_mode=" + std::to_string(static_cast<int>(a.traversal_mode)) +
                      ", extraction_type=" + std::to_string(static_cast<int>(a.extraction_type)) +
                      ", negate_image=" + std::to_string(a.negate_image) + ", dyn=" + std::to_string(a.dyn) +
                      ", size_mask=" + std::to_string(a.size_mask) +
                      ", double_exponential_alpha=" + std::to_string(a.double_exponential_alpha) +
                      ", simple_moving_average_memory=" + std::to_string(a.simple_moving_average_memory) +
                      ", exponential_moving_average_memory=" + std::to_string(a.exponential_moving_average_memory) +
                      ", one_euro_beta=" + std::to_string(a.one_euro_beta) +
                      ", one_euro_mincutoff=" + std::to_string(a.one_euro_mincutoff) +
                      ", one_euro_dcutoff=" + std::to_string(a.one_euro_dcutoff) +
                      ", bucket_size=" + std::to_string(a.bucket_size) +
                      ", nb_values_to_keep=" + std::to_string(a.nb_values_to_keep) +
                      ", discontinuity_relative=" + std::to_string(a.discontinuity_relative) +
                      ", discontinuity_absolute=" + std::to_string(a.discontinuity_absolute) +
                      ", minimum_for_fusion=" + std::to_string(a.minimum_for_fusion) +
                      ", default_sigma_position=" + std::to_string(a.default_sigma_position) +
                      ", default_sigma_thickness=" + std::to_string(a.default_sigma_thickness) +
                      ", default_sigma_luminosity=" + std::to_string(a.default_sigma_luminosity) +
                      ", min_nb_values_sigma=" + std::to_string(a.min_nb_values_sigma) +
                      ", sigma_pos_min=" + std::to_string(a.sigma_pos_min) +
                      ", sigma_thickness_min=" + std::to_string(a.sigma_thickness_min) +
                      ", sigma_luminosity_min=" + std::to_string(a.sigma_luminosity_min) +
                      ", gradient_threshold=" + std::to_string(a.gradient_threshold) +
                      ", llumi=" + std::to_string(a.llumi) + ", blumi=" + std::to_string(a.blumi) +
                      ", ratio_lum=" + std::to_string(a.ratio_lum) +
                      ", max_thickness=" + std::to_string(a.max_thickness) +
                      ", threshold_intersection=" + std::to_string(a.threshold_intersection) +
                      ", remove_duplicates=" + std::to_string(a.remove_duplicates) + ">";
             })
        .def("__doc__", []() { return "Holds parameters of the line detection"; });

    pybind11::class_<VSegment>(m, "VSegment")                                    //
        .def(pybind11::init<>())                                                 //
        .def(pybind11::init<int, int, int, int, int>())                          //
        .def_readwrite("label", &VSegment::label, "Label of the segment")        //
        .def_readwrite("x0", &VSegment::x0, "First coordinate of first point")   //
        .def_readwrite("y0", &VSegment::y0, "Second coordinate of first point")  //
        .def_readwrite("x1", &VSegment::x1, "First coordinate of second point")  //
        .def_readwrite("y1", &VSegment::y1, "Second coordinate of second point") //
        .def("__repr__",
             [](const VSegment& a) {
               return "<scribo.VSegment: label=" + std::to_string(a.label) + ", x0=" + std::to_string(a.x0) +
                      ", y0=" + std::to_string(a.y0) + ", x1=" + std::to_string(a.x1) + ", y1=" + std::to_string(a.y1) +
                      ">";
             })
        .def("__str__",
             [](const VSegment& a) {
               return std::to_string(a.label) + ": (" + std::to_string(a.x0) + ", " + std::to_string(a.y0) + ") -- (" +
                      std::to_string(a.x1) + ", " + std::to_string(a.y1) + ")";
             })
        .def("__doc__", []() { return "Holds vectorial information about detected lines"; });

    pybind11::class_<LSuperposition>(m, "LSuperposition")                                  //
        .def(pybind11::init<>())                                                           //
        .def(pybind11::init<int, int, int>())                                              //
        .def_readwrite("label", &LSuperposition::label, "Label of the line superposing")  //
        .def_readwrite("x", &LSuperposition::x, "First coordinate of the superposition")  //
        .def_readwrite("y", &LSuperposition::y, "Second coordinate of the superposition") //
        .def("__repr__",
             [](const LSuperposition& a) {
               return "<scribo.LSuperposition: label=" + std::to_string(a.label) + ", x=" + std::to_string(a.x) +
                      ", y=" + std::to_string(a.y) + ">";
             })
        .def("__str__",
             [](const LSuperposition& a) {
               return std::to_string(a.label) + ": (" + std::to_string(a.x) + ", " + std::to_string(a.y) + ")";
             })
        .def("__doc__", []() { return "Holds a label and a position."; });

    m.def("line_detector_vector", &details::line_detector_vector, "Perform scribo line detection");
    m.def("line_detector_pixel", &details::line_detector_pixel, "Perform scribo line detection");
    m.def("line_detector_full", &details::line_detector_full, "Perform scribo line detection");
  }
} // namespace pln::scribo