FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build
RUN ln -sv /usr/bin/python3 /usr/bin/python

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
WORKDIR /home/appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py --user && \
	rm get-pip.py

# install dependencies
# See https://pytorch.org/ for other options if you use a different version of CUDA
RUN pip install --user tensorboard cmake   # cmake from apt-get is too old
RUN pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install --user 'git+https://github.com/facebookresearch/fvcore'
# install detectron2
RUN git clone https://github.com/facebookresearch/detectron2 detectron2_repo
RUN pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.8/index.html

WORKDIR /home/appuser/detectron2_repo

COPY demo.py demo/demo.py
COPY predictor.py demo/predictor.py

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"

# RUN wget http://images.cocodataset.org/val2017/000000439715.jpg -O input.jpg

# run detectron2 under user "appuser":
# CMD python3 demo/demo.py --config-file configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml --input input.jpg --output outputs/output.json --opts MODEL.WEIGHTS detectron2://COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl MODEL.DEVICE cpu

CMD python3 demo/demo.py --config-file configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml --video-input mountdir/input.mp4 --output mountdir/video_output.json --opts MODEL.WEIGHTS detectron2://COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl MODEL.DEVICE cpu
