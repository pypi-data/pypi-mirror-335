add_library(pylene-numpy)
set_target_properties(pylene-numpy PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(pylene-numpy PUBLIC
                         $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                         $<INSTALL_INTERFACE:include>)
target_sources(pylene-numpy PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/image_cast.cpp
                                    ${CMAKE_CURRENT_SOURCE_DIR}/src/numpy_format.cpp
)
target_link_libraries(pylene-numpy PUBLIC pylene::core pybind11::pybind11)

# Waiting issue Pylene#101 is solved (https://gitlab.lre.epita.fr/olena/pylene/-/issues/101)
if (MSVC)
    target_compile_options(pylene-numpy PUBLIC "/Zc:preprocessor" "/permissive-")
endif (MSVC)