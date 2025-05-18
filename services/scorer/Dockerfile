FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/scorer/main.py ./main.py
COPY knowledge ./knowledge
CMD ["python", "main.py"]
