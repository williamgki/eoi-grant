FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir openai>=1.14.0 faiss-cpu
COPY services/scorer/main.py ./main.py
COPY knowledge ./knowledge
CMD ["python", "main.py"]
