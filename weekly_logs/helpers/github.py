import os
from github import Github, GithubException
from datetime import datetime, timedelta

# --- Configuration ---
# Either set GITHUB_TOKEN as an environment variable or replace os.getenv with your token string
# (NOT RECOMMENDED for security reasons if you share the script)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Example: "PyGithub/PyGithub" or "owner/repository-name"
REPO_NAME = "owner/repository-name"  # <--- CHANGE THIS TO YOUR TARGET REPO
OUTPUT_FILE = "repo_updates_last_week.txt"
DAYS_AGO = 7 # For the past week

# --- Helper Functions ---
def format_commit(commit):
    """Formats a commit object into a string."""
    commit_data = commit.commit
    author_name = commit_data.author.name
    commit_date = commit_data.author.date.strftime("%Y-%m-%d %H:%M:%S")
    message = commit_data.message.strip()
    sha_short = commit.sha[:7]
    files_changed = [f.filename for f in commit.files] if commit.files else ["N/A"]

    return (
        f"  Commit: {sha_short}\n"
        f"  Author: {author_name}\n"
        f"  Date: {commit_date}\n"
        f"  Message:\n{indent_text(message, 4)}\n"
        f"  Files Changed ({len(files_changed)}): {', '.join(files_changed[:5])}{'...' if len(files_changed) > 5 else ''}\n"
        # Add this line if you want the full diff, but it can be VERY long
        # f"  Diff:\n{indent_text(commit.files[0].patch if commit.files else 'N/A', 4)}\n" # Example for first file
    )

def format_issue_or_pr(item, is_pr=False):
    """Formats an issue or pull request object into a string."""
    item_type = "Pull Request" if is_pr else "Issue"
    title = item.title
    number = item.number
    user = item.user.login
    state = item.state
    created_at = item.created_at.strftime("%Y-%m-%d %H:%M:%S")
    updated_at = item.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    body = item.body.strip() if item.body else "No description provided."
    url = item.html_url

    details = (
        f"  {item_type} #{number}: {title}\n"
        f"  URL: {url}\n"
        f"  Author: {user}\n"
        f"  State: {state}\n"
        f"  Created: {created_at}\n"
        f"  Last Updated: {updated_at}\n"
        f"  Description:\n{indent_text(body, 4)}\n"
    )

    # Comments (updated in the last week)
    since_date_comments = datetime.utcnow() - timedelta(days=DAYS_AGO)
    comments_text = []
    comments = item.get_comments(since=since_date_comments) # Fetches comments updated since date
    for comment in comments:
        comment_author = comment.user.login
        comment_date = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        comment_body = comment.body.strip() if comment.body else "No comment body."
        comments_text.append(
            f"    Comment by {comment_author} on {comment_date}:\n{indent_text(comment_body, 6)}"
        )
    if comments_text:
        details += "  Recent Comments:\n" + "\n".join(comments_text) + "\n"

    if is_pr:
        pr_specifics = ""
        if item.merged:
            pr_specifics += f"  Merged: {item.merged_at.strftime('%Y-%m-%d %H:%M:%S')} by {item.merged_by.login if item.merged_by else 'N/A'}\n"
        pr_specifics += f"  Commits: {item.commits}\n"
        pr_specifics += f"  Changed Files: {item.changed_files}\n"
        # You can also fetch PR reviews and review comments if needed
        # reviews = item.get_reviews()
        # review_comments = item.get_review_comments()
        details += pr_specifics

    return details

def indent_text(text, spaces=2):
    """Indents a block of text."""
    prefix = " " * spaces
    return "".join([f"{prefix}{line}" for line in text.splitlines(True)])

# --- Main Logic ---
def main():
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it to your GitHub Personal Access Token.")
        return
    if REPO_NAME == "owner/repository-name":
        print("Error: REPO_NAME not configured. Please edit the script.")
        return

    print(f"Connecting to GitHub and fetching data for {REPO_NAME}...")
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
    except GithubException as e:
        print(f"Error connecting to GitHub or finding repository: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    since_date = datetime.utcnow() - timedelta(days=DAYS_AGO)
    print(f"Fetching updates since {since_date.strftime('%Y-%m-%d %H:%M:%S UTC')}...")

    output_content = []
    output_content.append(f"GitHub Repository Activity Report for: {repo.full_name}")
    output_content.append(f"Period: Last {DAYS_AGO} days (since {since_date.strftime('%Y-%m-%d')})")
    output_content.append(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    # 1. Commits in the last week
    output_content.append("--- Commits ---")
    try:
        commits = repo.get_commits(since=since_date)
        commit_count = 0
        for commit in commits:
            output_content.append(format_commit(commit))
            commit_count += 1
        if commit_count == 0:
            output_content.append("  No new commits in this period.\n")
        else:
            output_content.append(f"  Total new commits: {commit_count}\n")
    except GithubException as e:
        output_content.append(f"  Error fetching commits: {e}\n")
    except Exception as e:
        output_content.append(f"  An unexpected error occurred while fetching commits: {e}\n")


    # 2. Issues updated or created in the last week
    # (This will include PRs if not filtered, but we'll fetch PRs separately for more PR-specific details)
    output_content.append("--- Issues (Created or Updated) ---")
    try:
        issues = repo.get_issues(state="all", since=since_date, sort="updated", direction="desc")
        issue_count = 0
        for issue in issues:
            if not issue.pull_request: # Ensure it's an issue, not a PR
                output_content.append(format_issue_or_pr(issue, is_pr=False))
                issue_count += 1
        if issue_count == 0:
            output_content.append("  No issues created or updated in this period.\n")
        else:
            output_content.append(f"  Total issues active in period: {issue_count}\n")

    except GithubException as e:
        output_content.append(f"  Error fetching issues: {e}\n")
    except Exception as e:
        output_content.append(f"  An unexpected error occurred while fetching issues: {e}\n")

    # 3. Pull Requests updated or created in the last week
    output_content.append("--- Pull Requests (Created or Updated) ---")
    try:
        # get_issues can also fetch PRs and `since` works on updated_at for them
        # This is often more reliable for "active in period" than get_pulls' `since`
        pull_requests_as_issues = repo.get_issues(state="all", since=since_date, sort="updated", direction="desc")
        pr_count = 0
        for pr_issue in pull_requests_as_issues:
            if pr_issue.pull_request: # Ensure it's a PR
                try:
                    # We need to get the actual PullRequest object for more details
                    pr = repo.get_pull(pr_issue.number)
                    output_content.append(format_issue_or_pr(pr, is_pr=True))
                    pr_count +=1
                except GithubException as e_pr:
                    output_content.append(f"  Error fetching details for PR #{pr_issue.number}: {e_pr}\n")
                except Exception as e_pr_generic:
                    output_content.append(f"  Unexpected error for PR #{pr_issue.number}: {e_pr_generic}\n")

        if pr_count == 0:
            output_content.append("  No pull requests created or updated in this period.\n")
        else:
             output_content.append(f"  Total PRs active in period: {pr_count}\n")

    except GithubException as e:
        output_content.append(f"  Error fetching pull requests: {e}\n")
    except Exception as e:
        output_content.append(f"  An unexpected error occurred while fetching PRs: {e}\n")


    # (Optional) 4. Releases in the last week
    output_content.append("--- Releases ---")
    try:
        releases = repo.get_releases()
        release_count = 0
        for release in releases:
            # PyGithub doesn't directly support filtering releases by date before fetching all of them
            # So we fetch all and filter manually.
            if release.published_at and release.published_at >= since_date:
                output_content.append(
                    f"  Release: {release.tag_name} ({release.name})\n"
                    f"  Published: {release.published_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"  URL: {release.html_url}\n"
                    f"  Description:\n{indent_text(release.body.strip() if release.body else 'No description.', 4)}\n"
                )
                release_count += 1
        if release_count == 0:
            output_content.append("  No new releases in this period.\n")
        else:
            output_content.append(f"  Total new releases: {release_count}\n")

    except GithubException as e:
        output_content.append(f"  Error fetching releases: {e}\n")
    except Exception as e:
        output_content.append(f"  An unexpected error occurred while fetching releases: {e}\n")


    # Write to file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(output_content))
        print(f"\nSuccessfully wrote report to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error writing to file {OUTPUT_FILE}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing file: {e}")


if __name__ == "__main__":
    # --- IMPORTANT: Configure these ---
    # REPO_NAME = "PyGithub/PyGithub" # Example public repo
    # REPO_NAME = "kubernetes/kubernetes" # Example very active public repo
    REPO_NAME = "psf/requests" # Another example

    # Make sure GITHUB_TOKEN environment variable is set!
    # If you absolutely must hardcode (e.g., for a quick one-off test, NOT for shared code):
    # GITHUB_TOKEN = "your_pat_here"

    main()