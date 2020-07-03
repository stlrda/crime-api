# Python FastAPI for Serving Crime Data

FROM 

LABEL maintainer='Branson Fox <bransonfox@umsl.edu>'

# Environmental Variables

## For Connecting to DB
ENV DB_HOST='localhost'
ENV DB_PORT=5432
ENV USER='postgres'
ENV PASS='postgres'
ENV DB_NAME='crime'

# Install Python Dependencies
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/requirements.txt

RUN pip install -r requirements.txt

# Copy API Files
COPY main.py /api/main.py

# Start Uvicorn
CMD ["uvicorn", "main:app"]
