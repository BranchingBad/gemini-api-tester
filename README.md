# Gemini API Tester

This project provides a complete environment to test the Google Gemini API using both a simple **Flask web frontend** and a **standalone Python command-line interface (CLI) script**. It uses **Docker/Podman** for containerization to ensure a consistent and portable setup.

---

## 1. Prerequisites

You must have the following installed:

* **Python 3.9+** (For running the `gemini-test.py` script locally).
* **Docker or Podman** (For running the web application).
* **A Gemini API Key** (Set as an environment variable).

### Setting the GEMINI_API_KEY

The backend and CLI script both require the `GEMINI_API_KEY` environment variable to be set. The API key is stored as an enviroment variable for security.
More information can be found at https://ai.google.dev/gemini-api/docs/api-key

**Linux/macOS (For current session):**
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### Windows (Command Prompt):

```bash
set GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

## 2. Using the CLI Script (gemini-test.py)
The standalone Python script is useful for quick testing and benchmarking without running the full web server.

Installation
Install the necessary Python dependencies locally:

```bash
pip install -r requirements.txt
```

### Usage
Run the script directly from the command line.

### Option 1: Use the Default Model (gemini-2.5-flash)
Provide the prompt as a quoted argument after the script name.

```bash
python gemini-test.py "Explain the concept of containerization in one paragraph."
```

### Option 2: Specify a Model
Use the --model flag followed by the model name, and then the prompt.

```bash
python gemini-test.py --model gemini-2.5-pro "Write a short, dramatic monologue about a lost spaceman."
```

## 3. Running the Web UI with Podman/Docker
The web application is containerized using the provided Dockerfile and is designed to run on port 5000 inside the container.

### Step 1: Build the Container Image
This command builds the image, tags it as gemini-frontend, and passes your local GEMINI_API_KEY environment variable into the image using a build argument.

```bash
podman build -t gemini-frontend --build-arg GEMINI_API_KEY=$GEMINI_API_KEY .
# OR (for Docker)
# docker build -t gemini-frontend --build-arg GEMINI_API_KEY=$GEMINI_API_KEY .
```

### Step 2: Run the Container
Run the image, mapping the container's internal port 5000 to an external port (e.g., 8080) on your host machine. You can manually replace $GEMINI_API_KEY with your API key if you wish. It is recomened to use an enviroment variable (attackers can check command line history for previously used keys. Ask Gemini why this is best practice if you need).

```bash
podman run -d -p 8080:5000 --name gemini-app -e GEMINI_API_KEY=$GEMINI_API_KEY gemini-frontend
# OR (for Docker)
# docker run -d -p 8080:5000 --name gemini-app gemini-frontend
```

### Step 3: Access the Application
Open your web browser and navigate to:

http://localhost:8080

You can now use the interface to select models and send prompts.

Container Management
To stop and remove the running container:
```bash
podman stop gemini-app
podman rm gemini-app
# OR (for Docker)
# docker stop gemini-app
# docker rm gemini-app
```
