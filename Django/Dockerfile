FROM kubor/alpine-rdkit
RUN apk add --no-cache git && \
    mkdir /code
ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -U pip && \
    pip install -r requirements.txt && \
    pip install git+https://github.com/rdkit/django-rdkit.git
