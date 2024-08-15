FROM python:3.10.14-slim-bookworm
LABEL author=Max
RUN apt-get update &&  apt-get install -y && rm -rf /var/lib/apt/lists/*
WORKDIR /"MicroZip"
ADD https://github.com/zatomis/dev-zip.git .
#RUN pip install --no-cache-dir -r requirements.txt
#ENTRYPOINT ["python3", "main.py"]
