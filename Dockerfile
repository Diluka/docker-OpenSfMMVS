FROM diluka/sfm-base

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

ADD pipeline.py /usr/local/bin

WORKDIR /root

ENV PATH $PATH:/usr/local/bin/OpenMVS:/opt/OpenSfM/bin

