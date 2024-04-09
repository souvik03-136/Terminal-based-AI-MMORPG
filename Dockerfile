FROM python:3.9-slim

WORKDIR /app


RUN pip install google-generativeai python-dotenv


COPY . .

EXPOSE 8888

CMD ["python", "server.py"]
