### 🐳 Running the Project via Docker

```bash
# 1. Navigate to the project directory on your local host machine (Windows)
cd D:\Projects_Programming\DataEnginering\Data-Engineering-ZoomCamp2026\01-docker

# 2. Start an interactive Python 3.12 container
# - Override the default entrypoint to use bash
# - Mount the current directory (01-docker) to /app inside the container
docker run -it --entrypoint=bash -v "${PWD}:/app" python:3.12-slim

# 3. Navigate to the working directory inside the Linux container
cd app/test

# 4. Create a test file to verify the Linux environment (optional)
echo "Hello from Linux container" > file1.txt

# 5. Execute the script within the isolated container environment
python script.py

### 🚀 Local Setup with `uv`

```bash
# 1. Initialize project in current directory
python -m uv init --python 3.13

# 2. Add dependencies
python -m uv add pandas

# 3. Run scripts within isolated environment
python -m uv run python pipeline.py 12 329874