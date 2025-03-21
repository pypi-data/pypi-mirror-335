if(DEFINED ENV{VCPKG_ROOT})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" 
        CACHE STRING "Vcpkg toolchain file")
endif()

if(DEFINED ENV{VCPKG_INSTALLATION_ROOT})
  set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_INSTALLATION_ROOT}/scripts/buildsystems/vcpkg.cmake"
      CACHE STRING "Vcpkg toolchain file")
endif()

# if(APPLE)
#   set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "Build architectures for MacOS" FORCE)
# endif()



cmake_minimum_required(VERSION 3.15)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
# set(VCPKG_MANIFEST_MODE OFF)

project(flux_ws_module LANGUAGES CXX)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Include GNU install directories (defines CMAKE_INSTALL_LIBDIR, etc.)
include(GNUInstallDirs)

message(STATUS "TOOL: ${CMAKE_TOOLCHAIN_FILE}")
set(CMAKE_POLICY_DEFAULT_CMP0167 NEW)

# set(FLUX_WS_MODULE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/flux_ws_module")
# file(MAKE_DIRECTORY ${FLUX_WS_MODULE_DIR})

# find_package(pybind11 REQUIRED)
# set(PYBIND11_FINDPYTHON ON)
find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG)

# Find dependencies
find_package(Boost REQUIRED COMPONENTS 
     system 
     date_time 
     serialization
     algorithm
)
find_package(websocketpp REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(OpenSSL REQUIRED)

if(MSVC)
  add_compile_options(/std:c++20 /permissive-)
  add_compile_definitions(_WEBSOCKETPP_CPP11_RANDOM_DEVICE_)
  add_compile_options(/Zc:__cplusplus)  # Fix __cplusplus macro
endif()


pybind11_add_module(flux_ws_module
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BaseExchangeConnector.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/OkxConnector.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CryptoExtensions.cpp  
    ${CMAKE_CURRENT_SOURCE_DIR}/python_bindings/websocket_bindings.cpp
)
# Include directories
target_include_directories(flux_ws_module PRIVATE
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(flux_ws_module PRIVATE
    pybind11::module
    Boost::system 
    Boost::date_time
    OpenSSL::SSL 
    OpenSSL::Crypto
    websocketpp::websocketpp
    nlohmann_json::nlohmann_json
)

# TEST FILES
# Automatically include all .cpp files in src/tests/
# file(GLOB TEST_SOURCES "lib_tests/*.cpp")

# # Build each test as a separate executable
# foreach(test_source ${TEST_SOURCES})
#   get_filename_component(test_name ${test_source} NAME_WE)
#   add_executable(${test_name} ${test_source})
#   target_link_libraries(${test_name} PRIVATE 
#                         pybind11::embed
#                         Boost::system 
#                         Boost::date_time
#                         OpenSSL::SSL 
#                         OpenSSL::Crypto
#                         websocketpp::websocketpp
#                         nlohmann_json::nlohmann_json
#                         )
# endforeach()


set_target_properties(flux_ws_module PROPERTIES
    SUFFIX ""               # Remove default extension
    OUTPUT_NAME "_flux_ws_module"  # Set base name
)

# Platform-specific extensions (CMake will handle automatically)
if(WIN32)
    set_target_properties(flux_ws_module PROPERTIES SUFFIX ".pyd")
else()
    set_target_properties(flux_ws_module PROPERTIES SUFFIX ".so")
endif()

# Windows-specific settings
if(MSVC)
    add_compile_options(/bigobj)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

# ------------------------------------------------------------------
# Installation rules
#
# This install() command is required by scikit-build so that
# pip install . -v can run an "install" target.
#
# Here we install the built module to the standard library
# directory. scikit-build will later move it into the Python
# package directory.
install(TARGETS flux_ws_module
    LIBRARY DESTINATION flux_ws_module
    ARCHIVE DESTINATION flux_ws_module
    RUNTIME DESTINATION flux_ws_module
)