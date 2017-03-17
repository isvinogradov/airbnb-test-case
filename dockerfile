############################################################
# Dockerfile to build Python Application
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Ivan Vinogradov

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python3-dev python-distribute python3-pip

# Copy the application folder inside the container
RUN git clone https://github.com/isvinogradov/goggle /test_case_web_app
ADD /test_case_web_app /test_case_web_app

# Get pip to download and install requirements:
RUN pip3 install -r /test_case_web_app/requirements.txt

# Expose ports
EXPOSE 3008

# Set the default directory where CMD will execute
WORKDIR /test_case_web_app

# Set the default command to execute    
CMD python3 web.py