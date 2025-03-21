ARG argus_version=latest
FROM ghcr.io/uninett/argus:${argus_version}

RUN mkdir -p /extrapython
COPY ci_settings.py /extrapython/ci_settings.py
ENV PYTHONPATH=/extrapython
ENV DJANGO_SETTINGS_MODULE=ci_settings
