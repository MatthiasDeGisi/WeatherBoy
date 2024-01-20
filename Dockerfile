FROM python:3.11-bullseye
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
COPY data/update_channels.txt /app/data/
CMD ["python", "main.py"]