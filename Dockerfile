FROM ubuntu:16.04

RUN apt-get update 
RUN apt-get -y install \
    cmake \
    libpng-dev libjpeg-dev libtiff-dev libglu1-mesa-dev \
    libxxf86vm-dev libxxf86vm1 libxmu-dev libxi-dev libxrandr-dev gcc gcc-multilib \
    libopencv-dev \
    libboost-all-dev \
    libcgal-dev libcgal-qt5-dev \
    libatlas-base-dev libsuitesparse-dev \
    libgoogle-glog-dev \
    python-dev python-numpy python-opencv python-pip python-pyexiv2 python-pyproj python-scipy python-yaml \
    freeglut3-dev libglew-dev libglfw3-dev

# Install Eigen
ADD eigen /opt/eigen
RUN mkdir -p /opt/eigen_build && cd /opt/eigen_build \
    && cmake . /opt/eigen \
    && make && make install

# Install Ceres
ADD ceres-solver /opt/ceres-solver
RUN mkdir -p /opt/ceres_build \
    && cd /opt/ceres_build \
    && cmake . /opt/ceres-solver/ -DBUILD_TESTS=OFF -DBUILD_PYTHON=ON \
    && make && make install 

# Install OpenGV
ADD OpenGV /opt/OpenGV
RUN mkdir -p /opt/OpenGV_build \
    && cd /opt/OpenGV_build \
    && cmake . /opt/OpenGV/ -DCMAKE_C_FLAGS=-fPIC -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF \
    && make && make install 

ADD OpenSfM /opt/OpenSfM

RUN cd /opt/OpenSfM && \
    pip install -Ur requirements.txt && \
    python setup.py build

ADD VCG /opt/VCG
ADD OpenMVS /opt/OpenMVS
RUN mkdir -p /opt/OpenMVS_build \
    && cd /opt/OpenMVS_build \
    && cmake . /opt/OpenMVS -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="/opt/VCG" -DCMAKE_CXX_FLAGS="-w" \
    && make && make install

ENV PATH "/usr/local/bin/OpenMVS:/opt/OpenSfm/bin:${PATH}"

WORKDIR /root