from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import os
import datetime
import matplotlib.pyplot as plt
from scorer import calculate_score

# ---------------------------------
# App Setup
# ---------------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GITHUB_API = "https://api.github.com/users/"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# ---------------------------------
# Simple Cache (5 min)
# ---------------------------------

CACHE = {}
CACHE_DURATION = 300  # seconds


def get_cached(username):
    if username in CACHE:
        data, timestamp = CACHE[username]
        if (datetime.datetime.utcnow() - timestamp).total_seconds() < CACHE_DURATION:
            return data
    return None


def set_cache(username, data):
    CACHE[username] = (data, datetime.datetime.utcnow())


# ---------------------------------
# Commit Activity (REAL COMMITS)
# ---------------------------------

async def analyze_commit_activity(username, repos):

    six_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=180)

    total_commits = 0
    monthly_activity = {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            for repo in repos[:3]:  # limit for performance

                repo_name = repo.get("name")

                response = await client.get(
                    f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=50",
                    headers=HEADERS
                )

                if response.status_code != 200:
                    continue

                commits = response.json()

                for commit in commits:

                    commit_info = commit.get("commit", {})
                    author = commit_info.get("author", {})
                    date_str = author.get("date")

                    if not date_str:
                        continue

                    try:
                        commit_date = datetime.datetime.strptime(
                            date_str,
                            "%Y-%m-%dT%H:%M:%SZ"
                        )
                    except:
                        continue

                    if commit_date > six_months_ago:

                        total_commits += 1
                        month = commit_date.strftime("%Y-%m")

                        monthly_activity[month] = (
                            monthly_activity.get(month, 0) + 1
                        )

        return total_commits, monthly_activity

    except Exception:
        return 0, {}


# ---------------------------------
# Chart Generator (Always 6 Months)
# ---------------------------------

def generate_charts(language_data, monthly_activity):

    if not os.path.exists("static"):
        os.makedirs("static")

    # --------------------------
    # Language Distribution
    # --------------------------
    if language_data:
        plt.figure()
        plt.pie(
            language_data.values(),
            labels=language_data.keys(),
            autopct="%1.1f%%"
        )
        plt.title("Language Distribution")
        plt.savefig("static/language_chart.png")
        plt.close()

    # --------------------------
    # Commit Activity (Last 6 Months Always)
    # --------------------------

    today = datetime.datetime.utcnow()
    months_list = []

    for i in range(5, -1, -1):
        month_date = today - datetime.timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        months_list.append(month_str)

    commits = [monthly_activity.get(month, 0) for month in months_list]

    plt.figure()
    plt.bar(months_list, commits)
    plt.xticks(rotation=45)
    plt.title("Commit Activity (Last 6 Months)")
    plt.tight_layout()
    plt.savefig("static/commit_chart.png")
    plt.close()


# ---------------------------------
# Recruiter Summary
# ---------------------------------

def generate_ai_summary(score, total_commits):

    if score >= 85:
        grade = "A+ (Strong Hiring Signal)"
    elif score >= 70:
        grade = "A (Highly Competitive)"
    elif score >= 60:
        grade = "B (Moderate Hiring Signal)"
    else:
        grade = "C (Needs Optimization)"

    return f"""
Recruiter Evaluation Report

Grade: {grade}
Portfolio Score: {score}/100

Recent Commit Activity: {total_commits} commits in last 6 months

Recommendation:
Maintain consistent commits across months,
improve documentation depth,
and showcase impactful projects to improve hiring visibility.
"""


# ---------------------------------
# Routes
# ---------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "score": None,
        "strengths": [],
        "suggestions": [],
        "username": None,
        "ai_summary": None,
        "show_charts": False,
        "error": None
    })


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, github_url: str = Form(...)):

    username = github_url.rstrip("/").split("/")[-1]

    cached = get_cached(username)
    if cached:
        return templates.TemplateResponse("index.html", cached)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            user_resp = await client.get(
                f"{GITHUB_API}{username}",
                headers=HEADERS
            )

            if user_resp.status_code != 200:
                raise Exception("Invalid user")

            user_data = user_resp.json()

            repo_resp = await client.get(
                f"{GITHUB_API}{username}/repos?per_page=50",
                headers=HEADERS
            )

            repos = repo_resp.json()

    except Exception:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Invalid GitHub profile or rate limit exceeded.",
            "score": None,
            "strengths": [],
            "suggestions": [],
            "username": None,
            "ai_summary": None,
            "show_charts": False
        })

    # Process Repositories
    processed_repos = []
    language_data = {}

    for repo in repos[:10]:
        language = repo.get("language")

        if language:
            language_data[language] = language_data.get(language, 0) + 1

        processed_repos.append({
            "name": repo.get("name"),
            "stars": repo.get("stargazers_count", 0),
            "language": language,
            "has_readme": True
        })

    # Base Score
    score, strengths, suggestions = calculate_score(
        processed_repos, user_data
    )

    # Commit Analysis
    total_commits, monthly_activity = await analyze_commit_activity(username, repos)

    if total_commits > 20:
        score += 10
        strengths.append("Strong recent commit consistency.")
    else:
        suggestions.append("Increase commit consistency to demonstrate active development.")

    score = min(score, 100)

    # Generate Charts
    generate_charts(language_data, monthly_activity)

    # AI Summary
    ai_summary = generate_ai_summary(score, total_commits)

    response_data = {
        "request": request,
        "score": score,
        "strengths": strengths,
        "suggestions": suggestions,
        "username": username,
        "ai_summary": ai_summary,
        "show_charts": True,
        "error": None
    }

    set_cache(username, response_data)

    return templates.TemplateResponse("index.html", response_data)
