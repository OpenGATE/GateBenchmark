#!/bin/bash

set -e -x

#yum updates
if [ "$TEST" = "t15_optical" ] || [ "$TEST" = "t29_optical_digi" ]; then
   yum install -y  libxml2-devel
fi

#update python
yum install -y python39-pip.noarch
rm /usr/bin/python3 /usr/bin/pip3
ln -s /bin/python3.9 /usr/bin/python
ln -s /bin/python3.9 /usr/bin/python3
python3 -m pip install --upgrade pip
ln -s /bin/pip3.9 /usr/bin/pip3
which python3
python3 --version

#source /etc/mybashrc
export PATH=/software/cmake-3.18.4-Linux-x86_64/bin/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /software/geant4/install/bin/geant4.sh
source /software/root-cern/install/bin/thisroot.sh

#Install gatetools and clustertools
mkdir /software/gatetools
cd /software
git clone https://github.com/OpenGATE/GateTools.git gatetools
cd gatetools
pip3 install itk==5.3.0
pip3 install -e .
pip3 install uproot uproot3 xxhash lz4 pandas

#Install dependencies according the test
compile_torch=false
compile_rtk=false
export USE_OPTICAL=OFF
if [ "$TEST" = "t7_garf" ] || [ "$TEST" = "t9_gaga_phsp" ]; then
   compile_torch=true
fi
if [ "$TEST" = "t15_optical" ] || [ "$TEST" = "t29_optical_digi" ]; then
   export USE_OPTICAL=ON
fi
export GATE_USE_TORCH=OFF
if [ "$compile_torch" = true ] ; then
    cd /software
    mkdir torch
    cd torch
    wget https://download.pytorch.org/libtorch/cpu/libtorch-shared-with-deps-1.10.1%2Bcpu.zip
    unzip libtorch-shared-with-deps-1.10.1+cpu.zip
    rm -rf libtorch-shared-with-deps-1.10.1+cpu.zip
    export GATE_USE_TORCH=ON
    export TORCH_DIR=/software/torch/libtorch/share/cmake/Torch
fi
if [ "$TEST" = "t9_gaga_phsp" ] || [ "$TEST" = "t14_phsp_pairs" ]; then
    #install gaga
    pip3 install torch==1.10.0+cpu torchvision==0.11.1+cpu torchaudio==0.10.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
    cd /software
    mkdir gaga-phsp
    git clone https://github.com/dsarrut/gaga-phsp.git gaga-phsp
    cd gaga-phsp
    pip3 install -e .
fi
if [ "$TEST" = "t31_vpgTLE-tt" ]; then
    pip3 install hist
fi

# Compile master version of Gate
cd /software/gate
if [ -z "$COMMIT" ]; then
    COMMIT="develop"
fi
if [ ! -d /src ]; then
  git clone --branch ${COMMIT} https://github.com/OpenGATE/Gate.git /src
fi
cd bin
cmake -DGATE_USE_TORCH=$GATE_USE_TORCH \
      -DTorch_DIR=$TORCH_DIR \
      -DGATE_USE_OPTICAL=$USE_OPTICAL \
      /src
make -j4
cd ..
source /etc/mybashrc
echo 'export PATH=/software/gatetools/clustertools/:$PATH' >> /etc/mybashrc
echo 'export PATH=/software/gate/bin:$PATH' >> /etc/mybashrc
echo 'export PATH=/software/gatetools/clustertools/:$PATH' >> /etc/mybashrc
source /etc/mybashrc

# Go to execute the test
cd /home/
export LC_ALL=en_US.utf8
export LANG=en_US.utf8
pip3 install click colorama "numpy<2.0.0"
OutputTest=$(python3 runBenchmark.py -t ${TEST})
echo "$OutputTest"
OutputTest=$(echo "$OutputTest" | tail -1)
if [ "$OutputTest" != "True" ]; then
    exit -1
else
    exit 0
fi

