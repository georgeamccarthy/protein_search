# Get image for Python
FROM python:3.8

# Set working directory
WORKDIR /app/

# pip does not like being run as root, so create a user
RUN useradd --create-home jina

# Add the models folder locally to container
COPY ./models /app/models

# Give jina user permission to the folder
RUN chown jina models

# Add the tokernizers folder locally to container
COPY ./tokenizers /app/tokenizers

# Give jina user permission to the folder
RUN chown jina tokenizers

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
ADD ./src .

# Expose port
EXPOSE 8020

# Run the application
CMD [ "python", "src/app.py" ]