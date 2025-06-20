FROM python:3.12-slim AS builder 

ENV PYTHONUNBUFFERED=1

#Set working directory
WORKDIR /app

#Install system dependencies for mysqlclient & Pillow
RUN apt-get update && apt-get install -y \
gcc \
build-essential \
libssl-dev \
libffi-dev \
libxml2-dev \
libxslt1-dev \
zlib1g-dev \
libjpeg-dev \
pkg-config \ 
default-libmysqlclient-dev \
libmariadb-dev-compat \
libmariadb-dev \
  && rm -rf /var/lib/apt/lists/*

#Install pipenv first
RUN pip install --upgrade pip pipenv

#Install dependencies
COPY Pipfile Pipfile.lock /app/

#For development:
RUN pipenv install --system --deploy --dev 
#For production:
#RUN pipenv install --system --deploy --ignore-pipfile

#Copy full app
COPY . /app/

#Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

#Expose port
EXPOSE 8000

#Execute entrypoint.sh
CMD ["./docker-entrypoint.sh"]


#For development, run this:
#  docker compose --profile dev up --build

#For production, run: 
#  ./deploy.sh
