FROM ubuntu:latest

ENV WORKDIR="/collector"
WORKDIR $WORKDIR
ENV VIRTUAL_ENV="$WORKDIR/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
	&& apt-get install -y \
	python3 python3-venv python3-pip libsnmp-dev snmp-mibs-downloader vim \
	&& apt-get clean

#ENV HTTP_PROXY="http://20.220.3.113:8080"
#ENV HTTPS_PROXY="http://20.220.3.113:8080"
#ENV no_proxy=grafana

# Copy application
RUN mkdir config
RUN mkdir functions
RUN mkdir functions_core
RUN mkdir install
RUN mkdir keys
RUN mkdir telegraf
RUN mkdir license

ADD config config
ADD functions functions
ADD functions_core functions_core
ADD install install
ADD keys keys
ADD logs logs
ADD config/telegraf.conf telegraf
ADD main.py .

#RUN python3 -m pip install --upgrade pip
RUN python3 -m venv $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate

# Install dependencies:
ADD install/requirements.txt install
RUN pip3 install -r install/requirements.txt


# Run the application:
CMD ["python3", "main.py"]
