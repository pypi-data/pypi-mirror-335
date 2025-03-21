cmake_minimum_required(VERSION 3.23)
project(pylena CXX)

option(BUILD_PYLENA "Build the pylena_cxx module" ON)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)

find_package(pybind11 REQUIRED)
find_package(pylene REQUIRED)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/pylene-numpy)

if (BUILD_PYLENA)
    add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/pylena)
endif(BUILD_PYLENA)

include(GNUInstallDirs)

install(DIRECTORY pylene-numpy/include/pln TYPE INCLUDE)
install(TARGETS pylene-numpy)

if (BUILD_PYLENA)
    install(TARGETS pylena_cxx DESTINATION ".")
endif(BUILD_PYLENA)
