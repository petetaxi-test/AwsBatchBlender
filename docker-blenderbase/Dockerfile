FROM nvidia/cuda

# Largely based off https://github.com/ikester/blender-docker but updated
# to Blender 2.80, and include some additional dependencies
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
		unzip && \
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
ENV BLENDER_BZ2_URL https://download.blender.org/release/Blender2.80/blender-2.80-linux-glibc217-x86_64.tar.bz2

# Install Blender into /usr/local/blender
RUN mkdir /usr/local/blender && \
	curl -SL "$BLENDER_BZ2_URL" -o blender.tar.bz2 && \
	tar -jxvf blender.tar.bz2 -C /usr/local/blender --strip-components=1 && \
	rm blender.tar.bz2

