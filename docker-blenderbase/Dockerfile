FROM nvidia/cuda

# Largely based off https://github.com/ikester/blender-docker but updated
# to Blender 2.82a, and include some additional dependencies
LABEL authors="Peter Reay (peterareay@hotmail.com)"

# A base image including Blender and its dependencies. This is a 
# separate image to avoid long build times when changing the 
# scripts and python files

RUN apt-get update && \
	apt-get install -y \
		curl \
		bzip2 \
		libfreetype6 \
		libgl1-mesa-dev \
		libglu1-mesa \
		libxi6 \
		libxrender1 \
		zip \
		unzip \
		dos2unix \
		xz-utils && \
	apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/*

# python3 and the aws cli
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install awscli --upgrade --user
RUN pip3 install boto3
ENV PATH="~/.local/bin/aws:~/.local/bin:/usr/local/blender:${PATH}"
ENV PYTHONPATH="/root/scripts/:${PYTHONPATH}"

# Which version of Blender to install
ENV BLENDER_XZ_URL https://builder.blender.org/download/blender-2.83-7e9480b6cd74-linux64.tar.xz

# Install Blender into /usr/local/blender
RUN mkdir /usr/local/blender && \
	curl -SL "$BLENDER_XZ_URL" -o blender.tar.xz && \
	tar -Jxvf blender.tar.xz -C /usr/local/blender --strip-components=1 && \
	rm blender.tar.xz

