# Get image for Python
FROM python:3.8

# Set working directory
WORKDIR /app/

# pip does not like being run as root, so create a user
RUN useradd --create-home jina

# Add the data folder locally to container
COPY . .

# Switch to user
USER jina

# Path change needed for huggingface-cli and jina
ENV PYTHONPATH "${PYTHONPATH}:/home/jina/.local/bin"
ENV PATH "${PATH}:/home/jina/.local/bin"

# Is the application currently running in Docker?
ENV DOCKER "True"

# Add requirement contents
COPY ./requirements.txt requirements.txt
COPY ./requirements-pre.txt requirements-pre.txt

# Install dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-pre.txt

# Expose Port
EXPOSE 8501

# Run the application
CMD [ "streamlit", "run", "app.py" ]
