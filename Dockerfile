FROM python:3.9.0-slim

MAINTAINER abil <abilradhibilla@gmail.com>

WORKDIR /app

COPY . /app

EXPOSE 8080

RUN pip install flask==2.3.2

RUN pip install python-dotenv==1.0.0

RUN pip install openai==0.27.8

RUN pip install mysql-connector==2.2.9

CMD ["python3", "app.py"]
