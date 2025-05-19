FROM python:3.12-slim
WORKDIR /app

# Install FAISS system dependencies
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends libopenblas-dev gcc \ 
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/scorer/main.py ./main.py
COPY knowledge ./knowledge

CMD ["python", "main.py"]
