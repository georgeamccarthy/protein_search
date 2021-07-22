FROM jinaai/jina:master-standard
WORKDIR /app
COPY . .
EXPOSE 12345
RUN pip install -r requirements.txt && python app.py
ENTRYPOINT ["python", "app.py"]
