# Python FastAPI for Serving Crime Data

FROM python:3.8-slim-buster

LABEL maintainer='Branson Fox <bransonfox@umsl.edu>'

# Environmental Variables

## For Connecting to DB
ENV DB_HOST='localhost'
ENV DB_PORT=5432
ENV DB_USER='postgres'
ENV DB_PASS='postgres'
ENV DB_NAME='crime'

# Install Python Dependencies
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/requirements.txt

RUN pip install -r requirements.txt

# Copy API Files
COPY main.py /api/main.py
COPY models.py /api/models.py

EXPOSE 80

# Start Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
