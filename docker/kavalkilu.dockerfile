# Source: https://blog.alexellis.io/getting-started-with-docker-on-raspberry-pi/
FROM arm32v7/python:3.7.4-buster

RUN apt-get -q update \
    && apt-get -qy install \
    gcc \
    make \
    git \
    git-core \
    python3.7 \
    python3-pip \
    python3-dev \
    python3-pandas \
    python3-mysqldb \
    python3-rpi.gpio \
    python3-serial \
    && pip3 install Adafruit_DHT \
    sqlalchemy \
    selenium \
    amcrest \
    slackclient==1.3.1 \
    picamera \
    phue \
    pushbullet \
    roku \
    paramiko \
    beautifulsoup4

RUN git clone https://github.com/barretobrock/kavalkilu.git ./kavalkilu

RUN git clone git://git.drogon.net/wiringPi ./wiringPi \
    && cd wiringPi \
    && ./build

WORKDIR /home/pi
