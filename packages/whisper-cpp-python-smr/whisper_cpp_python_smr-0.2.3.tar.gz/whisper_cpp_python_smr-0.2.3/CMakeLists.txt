cmake_minimum_required(VERSION 3.21)

set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")
project(whisper_cpp)

set(BUILD_SHARED_LIBS "On")

set(GGML_BACKEND_DL "On")
set(GGML_NATIVE "Off")
set(GGML_SCHED_MAX_COPIES 10)


if(APPLE)
    set(GGML_METAL "On")
    set(GGML_METAL_EMBED_LIBRARY "On")
elseif(UNIX)
    set(GGML_OPENCL "On")
endif()

set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
set(CMAKE_SKIP_RPATH FALSE)


function(whisper_cpp_python_install_target target)
    install(
        TARGETS ${target}
        LIBRARY DESTINATION ${SKBUILD_PLATLIB_DIR}/whisper_cpp
        RUNTIME DESTINATION ${SKBUILD_PLATLIB_DIR}/whisper_cpp
        ARCHIVE DESTINATION ${SKBUILD_PLATLIB_DIR}/whisper_cpp
        FRAMEWORK DESTINATION ${SKBUILD_PLATLIB_DIR}/whisper_cpp
        RESOURCE DESTINATION ${SKBUILD_PLATLIB_DIR}/whisper_cpp
    )
    # Temporary fix for https://github.com/scikit-build/scikit-build-core/issues/374
    install(
        TARGETS ${target}
        LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/whisper_cpp
        RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/whisper_cpp
        ARCHIVE DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/whisper_cpp
        FRAMEWORK DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/whisper_cpp
        RESOURCE DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/whisper_cpp
    )
    set_target_properties(${target} PROPERTIES
        INSTALL_RPATH "$ORIGIN"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
    if(UNIX)
        if(APPLE)
            set_target_properties(${target} PROPERTIES
                INSTALL_RPATH "@loader_path"
                BUILD_WITH_INSTALL_RPATH TRUE
            )
        else()
            set_target_properties(${target} PROPERTIES
                INSTALL_RPATH "$ORIGIN"
                BUILD_WITH_INSTALL_RPATH TRUE
            )
        endif()
    endif()
endfunction()

add_subdirectory(vendor/whisper.cpp)
whisper_cpp_python_install_target(whisper)
whisper_cpp_python_install_target(ggml)
whisper_cpp_python_install_target(ggml-base)
whisper_cpp_python_install_target(ggml-cpu)
if(APPLE)
whisper_cpp_python_install_target(ggml-metal)
elseif(UNIX)
whisper_cpp_python_install_target(ggml-opencl)
endif()
