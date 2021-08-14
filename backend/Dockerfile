# Get image for Python
FROM python:3.8

# Set working directory
WORKDIR /app/

# pip does not like being run as root, so create a user
RUN useradd --create-home jina

# Add needed folders locally to container
COPY ./models /app/models
COPY ./tokenizers /app/tokenizers
COPY ./data /app/data
COPY ./embeddings /app/embeddings

# Give jina user permission to the folders
RUN chown jina models
RUN chown jina tokenizers
RUN chown jina data
RUN chown jina embeddings

# Switch to user
USER jina

# Path change needed for huggingface-cli and jina
ENV PYTHONPATH "${PYTHONPATH}:/home/jina/.local/bin"
ENV PATH "${PATH}:/home/jina/.local/bin"

# Copy the requirements over to the container
COPY ./requirements.txt /app/requirements.txt

# Install dependencies in the requirements
RUN pip3 install -r requirements.txt

# Add the src folder locally to container
ADD ./src /app/src

RUN python src/init.py

# Expose port
EXPOSE 8020

# Run the application
CMD ["python", "src/app.py" ]
