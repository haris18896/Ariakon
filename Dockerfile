# FROM python:3.12.4-alpine3.20
FROM python:3.12
LABEL maintainer='github.com/haris18896'

ENV PYTHONBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app

WORKDIR /app

EXPOSE 8000

ARG DEV=true

# Step 1: Set up virtual environment and upgrade pip
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip

# Step 2: Update package manager and install primary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client libjpeg-dev gfortran

# Step 3: Install temporary build dependencies (removed linux-headers-amd64)
RUN apt-get install -y --no-install-recommends \
    build-essential libpq-dev zlib1g-dev ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Step 4: Install required Python packages
RUN /py/bin/pip install -r /tmp/requirements.txt

# Step 5: Install development requirements if in DEV mode
RUN if [ "$DEV" = "true" ]; then \
      /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi

# Step 6: Clean up temporary files and cache
RUN rm -rf /tmp && \
    apt-get autoremove -y && \
    apt-get clean

# Step 7: Add Django user and set permissions
RUN adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

CMD ["run.sh"]
