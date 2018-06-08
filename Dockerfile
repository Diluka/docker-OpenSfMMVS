FROM diluka/sfm-base

# Install OpenGV
ADD OpenGV /opt/OpenGV
RUN mkdir -p /opt/OpenGV_build \
    && cd /opt/OpenGV_build \
    && cmake . /opt/OpenGV/ -DBUILD_TESTS=OFF -DBUILD_PYTHON=ON \
    && make -j && make install \
    && rm -rf /opt/OpenGV_build

ADD OpenSfM /opt/OpenSfM

RUN cd /opt/OpenSfM && \
    pip install -Ur requirements.txt && \
    python setup.py build

ADD VCG /opt/VCG
ADD OpenMVS /opt/OpenMVS
RUN mkdir -p /opt/OpenMVS_build \
    && cd /opt/OpenMVS_build \
    && cmake . /opt/OpenMVS -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="/opt/VCG" -DCMAKE_CXX_FLAGS="-w" \
    && make -j && make install \
    && rm -rf /opt/OpenMVS_build

WORKDIR /root

ENV PATH $PATH:/usr/local/bin/OpenMVS:/opt/OpenSfM/bin

