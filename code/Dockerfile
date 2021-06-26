# FROM nvidia/cuda:10.1-cudnn7-devel
FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get -y install \
	libpq-dev gcc python3-opencv ca-certificates python3-dev git wget sudo ninja-build

RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py && \
	rm get-pip.py

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

# install dependencies
# See https://pytorch.org/ for other options if you use a different version of CUDA
RUN pip install --user tensorboard cmake   # cmake from apt-get is too old
# RUN pip install --user torch==1.8.1 torchvision==0.9.1 torchaudio==0.8.1 -f https://download.pytorch.org/whl/cu101/torch_stable.html
RUN pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install --user 'git+https://github.com/facebookresearch/fvcore'
# install detectron2
RUN git clone https://github.com/facebookresearch/detectron2 detectron2_repo
# set FORCE_CUDA because during `docker build` cuda is not accessible
# ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
# ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
# ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.8/index.html
# RUN pip install --user -e detectron2_repo

RUN mkdir videos
RUN mkdir output

COPY detectron2/demo.py detectron2_repo/demo/demo.py
COPY detectron2/predictor.py detectron2_repo/demo/predictor.py

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY . .

EXPOSE 5000
CMD flask run --host=0.0.0.0
