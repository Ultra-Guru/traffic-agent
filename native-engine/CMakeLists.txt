cmake_minimum_required(VERSION 3.16)
project(traffic_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(BUILD_TESTS "Build native unit-test binary" ON)
option(BUILD_JNI "Build JNI shared library (Android/NDK)" OFF)

find_package(ZLIB REQUIRED)

set(ENGINE_SOURCES
    src/ip.cpp
    src/tcp.cpp
    src/udp.cpp
    src/dns.cpp
    src/sni.cpp
    src/http1.cpp
    src/http1flow.cpp
    src/http2.cpp
    src/ws.cpp
    src/quic.cpp
    src/md5.cpp
    src/tls.cpp
    src/hpack.cpp
    src/body.cpp
    src/multipart.cpp
    src/pcapng.cpp
    src/packet_build.cpp
    src/stack.cpp
    src/engine.cpp)

add_library(traffic_engine STATIC ${ENGINE_SOURCES})
target_include_directories(traffic_engine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(traffic_engine PUBLIC ZLIB::ZLIB)
if (CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(traffic_engine PRIVATE -Wall -Wextra)
endif()

if (BUILD_TESTS)
    enable_testing()
    add_executable(engine_tests
        tests/test_main.cpp
        tests/test_ip.cpp
        tests/test_tcp_udp.cpp
        tests/test_dns.cpp
        tests/test_sni.cpp
        tests/test_http1.cpp
        tests/test_http2.cpp
        tests/test_ws_quic.cpp
        tests/test_engine.cpp
        tests/test_md5.cpp
        tests/test_tls.cpp
        tests/test_hpack.cpp
        tests/test_body.cpp
        tests/test_multipart_pcapng.cpp
        tests/test_stack.cpp)
    target_link_libraries(engine_tests PRIVATE traffic_engine)
    add_test(NAME engine_tests COMMAND engine_tests)
endif()

if (BUILD_JNI)
    add_library(traffic_engine_jni SHARED src/jni.cpp)
    target_link_libraries(traffic_engine_jni PRIVATE traffic_engine ZLIB::ZLIB)
endif()
