# Webscraper and ETL Process for Crime Data

FROM rocker/geospatial:4.0.2

LABEL maintainer='Branson Fox <bransonfox@umsl.edu>'

# Environmental Variables

## For Connecting to DB
ENV DB_HOST='localhost'
ENV DB_PORT=5432
ENV USER='postgres'
ENV PASS='postgres'
ENV DB_NAME='crime'

## Optionally, Connect to Pushover
## Should be formatted '<user>:<app>'
ENV pushover=''

# Install Dependencies
RUN R -e "install.packages(c('compstatr', 'DBI', 'RPostgres', 'pushoverr', 'magrittr'))"

# Copy Script to Image
RUN mkdir /scripts
COPY scrape.R /scripts/

WORKDIR /scripts

# Execute
CMD ["R", "-e", "source('scrape.R')"]
