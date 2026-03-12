# JobTrackr-Ai

An AI-assisted job tracking application that helps collect, evaluate, and manage job opportunities from a centralized web interface.

---

## Overview

JobTrackr-Ai is a Python application built to support the job search process. It combines automated job discovery, AI-based evaluation, persistent job storage, and a Flask web interface for reviewing and managing results.

The application periodically searches for jobs based on user-defined criteria, evaluates newly discovered listings with a local LLM, and stores the results in a SQLite database for later review.

---

## Current Features

- Automated job search based on configured keywords, locations, and radius
- AI-powered job evaluation using a local LLM through Ollama
- SQLite-backed job database managed with SQLAlchemy
- Flask web interface for viewing and managing tracked jobs
- Background scheduler for periodic search runs
- Persistent user state to avoid unnecessary repeat runs

---

## Tech Stack

- Python
- Flask
- SQLAlchemy
- SQLite
- Selenium
- BeautifulSoup4
- Ollama

---

## Project Structure

```text
JobTrackr-Ai/
├── main.py
├── requirements.txt
├── app/                    # Flask app
├── core/                   # Core logic
│   ├── job_finder.py
│   ├── llm_evaluator.py
│   └── job_database.py
├── user/
│   ├── search_config.json
│   └── state.json
└── data/                   # Optional app data directory
```

---

## Requirements

- Python 3.x  
- Ollama installed locally  
- A supported browser and WebDriver for Selenium  

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/C47HERINE/JobTrackr-Ai.git
cd JobTrackr-Ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama:

```
https://ollama.com/download
```

On first use the project may download the configured model automatically.  
The default model can be changed in the evaluator configuration.

---

## Configuration

Before running the application, create or edit:

`user/search_config.json`

```json
{
  "keywords": ["python", "data scientist", "machine learning"],
  "locations": ["San Francisco", "New York", "Remote"],
  "radii": 25
}
```

Field descriptions:

- **keywords** – search terms used to find job listings  
- **locations** – target locations or remote options  
- **radii** – search radius for location-based results  

The application also uses `user/state.json` to track the last successful search run.

---

## Usage

Start the application:

```bash
python main.py
```

At startup the application will:

1. Load the user search configuration  
2. Run a scheduled job search cycle  
3. Evaluate newly discovered jobs with the LLM  
4. Save results to the database  
5. Start the Flask web interface  

The Flask app is typically available at:

```
http://127.0.0.1:5000
```

---

## How It Works

Each search cycle follows this process:

1. Load saved jobs from the database  
2. Search for jobs using the configured criteria  
3. Identify jobs that have not already been marked with a final decision  
4. Evaluate relevant jobs with the LLM  
5. Save new or updated records  
6. Update `user/state.json` with the latest run timestamp  

---

## Job Data

Tracked jobs may include:

- Indeed ID  
- Title  
- Company  
- Link  
- Location  
- Job type  
- Skills  
- Description  
- AI recommendation  
- AI answer  
- Timestamp  
- Application status  
- City  

---

## Roadmap

Planned features include:

- LLM-tailored CV generation based on selected job postings from the web app  
- LLM mock interview support  
- A settings route to manage user configuration and app data from the web interface  
- A chat tab for direct interaction with the AI for broader job-search guidance  
- A dedicated interview tracking page  
- Search and filtering tools for interview preparation  
- Automated application workflows for supported platforms  
- User authentication and per-user data separation  

---

## Notes

- This project is under active development.
- Some planned features are not yet implemented.
- Current behavior may change as the application evolves.

---

## License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

## Author

Created by **C47HERINE**

GitHub:  
https://github.com/C47HERINE