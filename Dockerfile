FROM ubuntu:22.04

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y python3.11 python3-pip && pip install --upgrade pip && pip install -r requirement.txt

EXPOSE 8501

CMD ["streamlit", "run", "front.py", "--server.port", "8501"]