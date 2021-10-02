FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /backend
ADD requirements.txt /backend/

RUN pip install -r requirements.txt
ADD . /backend/


COPY entrypoint.sh /backend/
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/backend/entrypoint.sh"]