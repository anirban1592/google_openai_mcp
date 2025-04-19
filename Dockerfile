FROM python:3.13-slim

# Set the working directory
WORKDIR /app

RUN pip install uv

# Copy the current directory contents into the container at /app
COPY . /app


RUN uv venv .venv



CMD ["sh", "-c", "cd openai-agent && uv run agent.py"]