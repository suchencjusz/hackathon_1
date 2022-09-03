FROM python:3.8-slim-buster

EXPOSE 5555

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "server2.py"]