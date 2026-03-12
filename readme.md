I'll start by exploring the repository to understand its structure and purpose, then create a comprehensive README file.Let me get more details about the key files in the project:Perfect! I now have the information I need to write a comprehensive README for the JobTrackr-Ai repository. Let me create a professional README file based on the code structure and functionality.

```markdown name=README.md
# JobTrackr-Ai

An intelligent job application tracking system that uses AI to help manage, evaluate, and apply to job opportunities automatically.

## Overview

JobTrackr-Ai is a Python-based application designed to streamline the job search process. It combines automated job searching, AI-powered job evaluation, and application management in a centralized web interface. The system continuously monitors job listings, evaluates them against your preferences, and assists with the application process.

## Features

- **Automated Job Search**: Periodically searches for job listings based on your configured keywords, locations, and search radius
- **AI-Powered Evaluation**: Uses AI to evaluate job opportunities and provide recommendations
- **Job Database**: Stores and manages all discovered job opportunities with their evaluation status
- **Web Interface**: Flask-based web application for viewing and managing job applications
- **Background Processing**: Runs continuous job search in a background thread without blocking the main application
- **State Management**: Tracks search history and configuration to avoid duplicate searches

## Tech Stack

- **Backend Framework**: Flask
- **Database**: SQLAlchemy with SQLite
- **Web Scraping**: BeautifulSoup4, Selenium
- **HTTP Requests**: Requests library
- **Language**: Python 3.x

## Project Structure

```
JobTrackr-Ai/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── app/                    # Flask application module
├── core/                   # Core business logic
│   ├── JobFinder          # Job search functionality
│   ├── Evaluator          # AI-powered job evaluation
│   └── JobRepository      # Database operations
├── data/                   # Data storage and configuration
└── user/                   # User configuration and state
    ├── state.json         # Last run timestamp and user state
    └── search_config.json # Search preferences (keywords, locations, radius)
```

## Installation

0. **Install Ollama**
   https://ollama.com/download
   The projects integrates an LLM that's running using Ollama. On first run it will download and set Gemma3:12b automatically. The model can be changed, but be aware that it has been chosen for its reasoning and mulimidal capabilities.
   Although the system requirements for the core system are low, at least 12gb of vram is needed to run Gemma3:12 qKM.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/C47HERINE/JobTrackr-Ai.git
   cd JobTrackr-Ai
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the application, configure your job search preferences:

### `user/search_config.json`

Create or update this file with your search criteria:

```json
{
  "keywords": ["python", "data scientist", "machine learning"],
  "locations": ["San Francisco", "New York", "Remote"],
  "radii": 25
}
```

- **keywords**: Job titles, skills, or industries to search for
- **locations**: Geographic locations or remote work options
- **radii**: Search radius in miles (applies to location-based searches)

## Usage

Run the application:

```bash
python main.py
```

The application will:
1. Start a background thread that continuously searches for jobs every 6 hours
2. Launch the Flask web server (typically accessible at `http://localhost:5000`)
3. Evaluate new jobs using AI and save results to the database
4. Track application state in `user/state.json`

## How It Works

### Job Search Cycle

1. **Periodic Search**: The background thread checks if 6 hours have elapsed since the last search
2. **Job Discovery**: Searches job boards using configured keywords and locations
3. **New Job Filtering**: Identifies jobs that haven't been evaluated yet
4. **AI Evaluation**: Uses the Evaluator to assess job fit and provide recommendations
5. **Database Update**: Saves evaluated jobs with their assessment status
6. **State Tracking**: Updates the last run timestamp to prevent duplicate searches

### Job Statuses

Jobs are tracked with decision statuses:
- **New**: Just discovered, awaiting evaluation
- **Apply**: Recommended by AI, ready to apply
- **Pass**: Not a good fit based on evaluation
- **Error**: Will be reevaluated on next run (if the LLM does not answer properly)

## Planned Features (TODOs)

- [ ] Add dedicated route/page for jobs with interviews to track interview progress
- [ ] Create search route/page to target specific job data for interview preparation
- [ ] Automated application submission to Indeed via Selenium
- [ ] Enhanced database logging for:
  - Job applications submitted
  - Jobs pending manual offline application
  - Jobs where AI answered "no"
- [ ] User authentication and login route
- [ ] User-specific database per account

## Dependencies

- **beautifulsoup4**: Web scraping HTML parsing
- **selenium**: Browser automation for job applications
- **requests**: HTTP library for API calls
- **Flask**: Web framework
- **SQLAlchemy**: ORM and database toolkit
- **flask-sqlalchemy**: Flask integration for SQLAlchemy

## Database

The application uses SQLAlchemy with a local SQLite database for job storage. The JobRepository class handles all database operations including:
- Saving and loading jobs
- Tracking job application status
- Maintaining search history

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is currently unlicensed.

## Author

Created by [C47HERINE](https://github.com/C47HERINE)

---

**Note**: This is an active development project. Features and functionality are subject to change.
```