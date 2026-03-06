FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r backend/requirements.txt

RUN chmod +x start.sh

CMD ["bash", "start.sh"]