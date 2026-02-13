# GitHub Portfolio Analyzer

A FastAPI-based web application that analyzes GitHub profiles to provide a comprehensive portfolio score, recruiter evaluation report, and activity visualizations.

## Features

- **Portfolio Scoring**: Calculates a score (0-100) based on repository count, README quality, stars, activity, and language diversity.
- **Commit Analysis**: Analyzes real commit data from the last 6 months to track consistency.
- **Visualizations**: Generates charts for language distribution and commit activity using Matplotlib.
- **Recruiter Evaluation**: Provides a graded report with strengths, suggestions, and hiring signals.
- **Caching**: Implements a simple 5-minute cache to optimize API usage and performance.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 Templates, HTML/CSS
- **Analysis**: HTTPX (Async GitHub API requests), Matplotlib (Charts)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AI_Github
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

4. (Optional) Set a GitHub Token to avoid rate limits:
   ```bash
   set GITHUB_TOKEN=your_token_here
   ```

## Usage

1. Navigate to the `app` directory:
   ```bash
   cd app
   ```

2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser and go to `http://127.0.0.1:8000`.
4. Enter a GitHub profile URL to begin analysis.
