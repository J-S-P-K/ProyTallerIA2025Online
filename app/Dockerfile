# syntax=docker/dockerfile:1
FROM python:3.10.11
WORKDIR /docs
ENV FLASK_APP=backend.py
ENV FLASK_RUN_HOST=0.0.0.0
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .
#RUN cd /docs
#RUN flask --app app run
CMD ["python", "app.py"]

#CMD ["python","/docs/static/chat.py"]
