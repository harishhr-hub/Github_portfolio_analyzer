def calculate_score(repos, user_data):
    score = 0
    suggestions = []
    strengths = []

    total_repos = len(repos)

    # 1️⃣ Repository Count
    if total_repos >= 5:
        score += 15
        strengths.append("Good number of repositories.")
    else:
        suggestions.append("Add more public repositories to showcase skills.")

    # 2️⃣ README Check
    readme_count = sum(1 for repo in repos if repo["has_readme"])
    if readme_count >= total_repos * 0.6:
        score += 20
        strengths.append("Most repositories contain README files.")
    else:
        suggestions.append("Add proper README files explaining project purpose and tech stack.")

    # 3️⃣ Stars
    stars = sum(repo["stars"] for repo in repos)
    if stars > 5:
        score += 15
        strengths.append("Projects show community engagement (stars).")
    else:
        suggestions.append("Improve project quality and promote them to gain stars.")

    # 4️⃣ Activity
    if user_data["public_repos"] > 3:
        score += 20
        strengths.append("Profile shows consistent project activity.")
    else:
        suggestions.append("Maintain consistent commits to show active development.")

    # 5️⃣ Language Diversity
    languages = set(repo["language"] for repo in repos if repo["language"])
    if len(languages) >= 2:
        score += 15
        strengths.append("Good language diversity.")
    else:
        suggestions.append("Try working with multiple technologies to show versatility.")

    # Final Score Scaling
    final_score = min(score, 100)

    return final_score, strengths, suggestions
