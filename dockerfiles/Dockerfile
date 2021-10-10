FROM python:3.9.6-buster
# FROM latonaio/l4t-ds-opencv-7.2:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=random-voice-streaming-periodic \
    AION_HOME=/var/lib/aion

RUN mkdir ${AION_HOME}
WORKDIR ${AION_HOME}
# Setup Directoties
RUN mkdir -p \
    $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/

# Install UVC Driver Gstreamer
# Add libcanberra-gtk-module libcanberra-gtk3-module
RUN apt-get update && apt-get install -y \
    ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY . .
# COPY requirements.txt .
RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "main.py"]
