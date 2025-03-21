FROM quay.io/pypa/manylinux2014_aarch64
RUN git clone --recursive https://github.com/KhronosGroup/OpenCL-SDK.git && \
    cd OpenCL-SDK && \
    cmake -B build -DCMAKE_INSTALL_PREFIX=dist -D BUILD_TESTING=OFF -D BUILD_DOCS=OFF -D BUILD_EXAMPLES=OFF -D BUILD_TESTS=OFF -D OPENCL_SDK_BUILD_SAMPLES=OFF -D OPENCL_SDK_TEST_SAMPLES=OFF && \
    cd build \
    make -j$(nproc) && \
    make -j$(nproc) install
FROM quay.io/pypa/manylinux2014_aarch64
COPY --from=0 /OpenCL-SDK/dist/ /usr/
