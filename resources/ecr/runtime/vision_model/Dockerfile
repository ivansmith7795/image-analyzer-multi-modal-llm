FROM nvcr.io/nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt update && \
    apt install -y wget git && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir .conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN conda init bash

RUN pip install --upgrade pip
RUN pip install --upgrade numpy setuptools wheel
RUN pip install torch==2.2.1+cu118 torchvision==0.17.1+cu118 --index-url https://download.pytorch.org/whl/cu118

RUN apt update
RUN apt install build-essential -y
RUN apt install cuda-toolkit-11-8 -y

RUN git clone https://github.com/AutoGPTQ/AutoGPTQ.git
WORKDIR /AutoGPTQ

ARG TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6+PTX;8.9;9.0" 
RUN python setup.py build
RUN pip install -vvv .

RUN pip install pillow boto3 flask einops

# Add our inference source
ADD src src

# Update PATH environment variable to include /opt/program directory
ENV PATH="/opt/program:${PATH}"

# Set the working directory in the Docker image to /opt/program
WORKDIR /opt/program

# Copy the source code of the application
COPY ./src /opt/program

ENTRYPOINT ["python", "inference.py"]