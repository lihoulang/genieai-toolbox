FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN sed -i 's/dashscope==1.20.15/dashscope==1.20.14/' requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 30005

# 关键修复：用 uvicorn 启动，不是 gunicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30005"]

