FROM python:3.11-bullseye
COPY requirements.txt /app/
COPY data/update_channels.txt /app/data/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]