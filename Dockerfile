FROM ubuntu:22.04

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN apt-get update
RUN apt-get install -y python3.11 python3-pip 
RUN pip install --upgrade pip
RUN pip install -r requirement.txt

EXPOSE 8504

CMD ["streamlit", "run", "front.py", "--server.port", "8504"]