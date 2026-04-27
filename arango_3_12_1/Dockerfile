FROM python:3.6.2

WORKDIR "/tests"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY tests/ .