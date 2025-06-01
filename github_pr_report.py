import requests
import datetime
import argparse
import os # For potential API token

TARGET_REPO = "geohot/tinygrad"
DAYS_ACTIVE = 7
GITHUB_API_URL = "https://api.github.com"
# Consider adding a placeholder for GITHUB_TOKEN
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_pull_requests(repo_name, api_token): # num_days is no longer used for initial fetch
    """
    Fetches all open pull requests from the specified GitHub repository.
    Further filtering by activity date will be done based on PR's update date,
    comments, and commits.
    """
    # since_date = datetime.datetime.now() - datetime.timedelta(days=num_days) # Not used here anymore
    # since_date_str = since_date.isoformat() # Not used here anymore

    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if api_token:
        headers["Authorization"] = f"token {api_token}"

    params = {
        "state": "open",  # Fetch only open PRs
        "sort": "updated", # Sort by update date to get most recently active ones first
        "direction": "desc",
        "per_page": 100,
    }

    all_pulls = []
    page = 1
    print(f"Fetching open PRs from {url}...")
    while True:
        params["page"] = page
        # print(f"Fetching page {page} with params: {params}") # Less verbose
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            current_pulls = response.json()
            if not current_pulls:
                break
            all_pulls.extend(current_pulls)
            if len(current_pulls) < params["per_page"]: # last page
                break
            page += 1
            if page > 10: # Increased safety break for potentially many open PRs
                print("Reached max pages (10) for fetching open PRs.")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching open pull requests: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.content}")
            return None # Return None on error

    print(f"Fetched a total of {len(all_pulls)} open PRs.")
    return all_pulls

# Make sure this function is defined in github_pr_report.py, replacing the placeholder
def get_recent_comments(pr_number, repo_name, api_token, num_days):
    """
    Fetches recent comments for a specific pull request (issue).
    Comments are filtered if they were updated within the last num_days.
    """
    base_url = f"{GITHUB_API_URL}/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if api_token:
        headers["Authorization"] = f"token {api_token}"

    # Calculate the 'since' date for filtering comments
    since_date_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=num_days)
    since_date_iso_str = since_date_dt.isoformat()

    params = {
        "since": since_date_iso_str, # Filters comments updated at or after this time
        "sort": "updated",      # Sort by update date (though 'since' makes this less critical for filtering)
        "direction": "desc",    # Get most recently updated first (good for display if not re-sorting)
        "per_page": 100,        # Max per page
    }

    print(f"Fetching comments for PR #{pr_number} in {repo_name} updated since {since_date_iso_str}...")

    all_comments_details = []
    current_page = 1
    max_pages_to_fetch = 3 # Safety limit for pagination

    try:
        while current_page <= max_pages_to_fetch:
            params["page"] = current_page
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            comments_page = response.json()

            if not comments_page: # No more comments
                break

            for comment in comments_page:
                # The 'since' parameter filters by 'updated_at'.
                # No need for an additional client-side check of `comment_updated_at >= since_date_dt`
                # if API's 'since' param for issue comments behaves as documented (filters by update time).
                # GitHub API docs: "Only comments updated at or after this time are returned."
                all_comments_details.append({
                    "id": comment["id"],
                    "user": comment["user"]["login"] if comment["user"] else "N/A",
                    "body": comment["body"],
                    "created_at": comment["created_at"],
                    "updated_at": comment["updated_at"],
                    "html_url": comment["html_url"],
                })

            if len(comments_page) < params["per_page"]: # Last page of comments
                break

            current_page += 1
            # Check if max_pages_to_fetch has been exceeded (if we fetched exactly max_pages_to_fetch)
            if current_page > max_pages_to_fetch:
                print(f"Reached max comment pages ({max_pages_to_fetch}) for PR #{pr_number}.")
                break

        print(f"Found {len(all_comments_details)} relevant comments for PR #{pr_number} (updated since {since_date_iso_str}).")
        return all_comments_details

    except requests.exceptions.RequestException as e:
        print(f"Error fetching comments for PR #{pr_number} from {repo_name}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}, content: {e.response.content}")
        return [] # Return empty list on error
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred while fetching comments for PR #{pr_number}: {e}")
        return []

# Make sure this function is defined in github_pr_report.py, replacing the placeholder
def get_recent_commits(pr_number, repo_name, api_token, num_days):
    """
    Fetches recent commits for a specific pull request.
    Commits are filtered if their author date is within the last num_days.
    """
    base_url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if api_token:
        headers["Authorization"] = f"token {api_token}"

    since_filter_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=num_days)

    params = {
        "per_page": 100, # Max per page
    }

    print(f"Fetching commits for PR #{pr_number} in {repo_name}...")

    all_commits_details = []
    current_page = 1
    # This endpoint lists a maximum of 250 commits for a pull request.
    # Fetching 3 pages with per_page=100 covers this (100+100+up to 50).
    max_pages_to_fetch = 3

    try:
        while current_page <= max_pages_to_fetch:
            params["page"] = current_page
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            commits_page = response.json()

            if not commits_page: # No more commits
                break

            for commit_data in commits_page:
                commit_details = commit_data.get('commit', {})
                author_date_str = commit_details.get('author', {}).get('date')
                committer_date_str = commit_details.get('committer', {}).get('date')

                commit_date_str = author_date_str or committer_date_str

                if not commit_date_str:
                    # print(f"Skipping commit in PR #{pr_number} due to missing date: {commit_data.get('sha')}")
                    continue

                # Ensure commit_date_dt is timezone-aware (UTC)
                commit_date_dt = datetime.datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))

                if commit_date_dt >= since_filter_dt:
                    author_info = commit_details.get('author', {})
                    # Use GitHub login if available from the top-level author field, else use name from commit data
                    github_author_login = None
                    if commit_data.get('author'): # 'author' field at the commit list level (contains GitHub user)
                         github_author_login = commit_data.get('author', {}).get('login')

                    commit_author_name = author_info.get('name', 'N/A') # from commit.commit.author.name

                    all_commits_details.append({
                        "sha": commit_data["sha"],
                        "author_name": github_author_login or commit_author_name, # Prefer GitHub login
                        "message": commit_details.get("message", "No commit message"),
                        "date": commit_date_str, # Store original string for direct use or re-parsing
                        "html_url": commit_data.get("html_url", "#"), # URL to the commit itself
                    })

            if len(commits_page) < params["per_page"]: # Last page of commits
                break

            current_page += 1
            # No need to check current_page > max_pages_to_fetch inside loop, while condition handles it

        print(f"Found {len(all_commits_details)} relevant commits for PR #{pr_number} in the last {num_days} days.")
        return all_commits_details

    except requests.exceptions.RequestException as e:
        print(f"Error fetching commits for PR #{pr_number} from {repo_name}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}, content: {e.response.content}")
        return []
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred while fetching commits for PR #{pr_number}: {e}")
        return []

def process_pr_data(pull_requests_json, repo_name):
    """
    Processes the raw JSON data of pull requests to extract relevant information.
    It also processes the 'fetched_comments' and 'fetched_commits' attached to pr_data.
    """
    processed_prs = []
    if not pull_requests_json:
        return processed_prs

    for pr_data in pull_requests_json:
        pr_state = pr_data['state']
        if pr_state == 'closed' and pr_data['merged_at']:
            pr_state = 'merged'

        author = pr_data['user']['login'] if pr_data['user'] else 'N/A'

        processed_info = {
            "number": pr_data['number'],
            "title": pr_data['title'],
            "author": author,
            "state": pr_state,
            "created_at": pr_data['created_at'],
            "updated_at": pr_data['updated_at'],
            "closed_at": pr_data['closed_at'],
            "merged_at": pr_data['merged_at'],
            "html_url": pr_data['html_url'],
            "comments": pr_data.get('comments', 0), # Overall comment count on PR
            "body": pr_data.get('body', ''), # Ensure PR body is carried over
        }

        # Update summaries based on actual fetched data
        comments_list = pr_data.get('fetched_comments', [])
        commits_list = pr_data.get('fetched_commits', [])
        processed_info["fetched_comments_summary"] = f"{len(comments_list)} recent comment(s)" if comments_list else "No recent comments"
        processed_info["fetched_commits_summary"] = f"{len(commits_list)} recent commit(s)" if commits_list else "No recent commits"

        # Storing the detailed lists too, for generate_report
        processed_info["fetched_comments_details"] = comments_list
        processed_info["fetched_commits_details"] = commits_list

        processed_prs.append(processed_info)
    return processed_prs

def format_date(date_str):
    """Formats an ISO date string to a more readable format."""
    if not date_str:
        return "N/A"
    try:
        dt_obj = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
    except ValueError: # Handle cases where date_str might not be a full ISO format, e.g. if already formatted
        return date_str

def generate_report(processed_prs_list, repo_name, num_days):
    """
    Generates a formatted string report from the processed PR data,
    including details of recent comments and commits.
    """
    report_lines = []
    report_lines.append(f"PR Activity Report for {repo_name} - Last {num_days} Days (Based on Open PRs with activity)")
    report_lines.append("=" * (len(report_lines[0])))

    active_open_prs = [pr for pr in processed_prs_list if pr['state'] == 'open'] # Should be all, given current filtering

    report_lines.append(f"\n--- Active Open PRs ({len(active_open_prs)}) ---")
    if active_open_prs:
        for pr in active_open_prs:
            report_lines.append(
                f"\n  PR #{pr['number']}: {pr['title']}\n"
                f"    Author: {pr['author']}, Created: {format_date(pr['created_at'])}, Last Updated: {format_date(pr['updated_at'])}\n"
                f"    URL: {pr['html_url']}"
            )

            # PR Body
            pr_body = pr.get('body')
            if pr_body and pr_body.strip():
                # Replace multiple newlines/carriage returns with a single space for snippet
                body_cleaned = ' '.join(pr_body.strip().split())
                body_snippet = body_cleaned[:200] + ("..." if len(body_cleaned) > 200 else "")
                report_lines.append(f"    Body: {body_snippet}")
            else:
                report_lines.append("    Body: (No body provided)")

            # Recent Comments
            comments = pr.get('fetched_comments_details', [])
            # report_lines.append(f"    Activity - {pr.get('fetched_comments_summary', 'Comments: N/A')}") # Redundant if details are listed
            if comments:
                report_lines.append(f"    Recent Comments ({len(comments)}):")
                for comment in comments:
                    comment_body_cleaned = ' '.join(comment.get('body', '').strip().split())
                    comment_body_snippet = comment_body_cleaned[:150] + ("..." if len(comment_body_cleaned) > 150 else "")
                    report_lines.append(
                        f"      - By {comment.get('user', 'N/A')} on {format_date(comment.get('updated_at'))}: "
                        f"\"{comment_body_snippet}\"\n" # Add quotes for clarity
                        f"        URL: {comment.get('html_url', '#')}"
                    )

            # Recent Commits
            commits = pr.get('fetched_commits_details', [])
            # report_lines.append(f"    Activity - {pr.get('fetched_commits_summary', 'Commits: N/A')}") # Redundant if details are listed
            if commits:
                report_lines.append(f"    Recent Commits ({len(commits)}):")
                for commit in commits:
                    commit_message_snippet = commit.get('message', '').split('\n')[0][:100] # First line, max 100 chars
                    commit_message_snippet += "..." if len(commit.get('message', '')) > 100 or '\n' in commit.get('message', '') else ""
                    report_lines.append(
                        f"      - By {commit.get('author_name', 'N/A')} on {format_date(commit.get('date'))}: "
                        f"\"{commit_message_snippet}\"\n" # Add quotes
                        f"        SHA: {commit.get('sha', 'N/A')}, URL: {commit.get('html_url', '#')}"
                    )
            elif not comments: # If there are no comments AND no commits, state that explicitly.
                 report_lines.append("    No recent comments or commits.")

            report_lines.append("-" * 60) # Separator for PRs (increased length)

    else:
        report_lines.append("  No open PRs with activity in this period.")

    report_lines.append("\n" + "=" * (len(report_lines[0])))
    report_lines.append(f"Total Active Open PRs reported with activity in the last {num_days} days: {len(active_open_prs)}")
    # Removed: report_lines.append(f"Total PRs processed for activity in the last {num_days} days: {len(processed_prs_list)}")
    # as it's the same as active_open_prs in current logic

    return "\n".join(report_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a report of PR activity on a GitHub repository.")
    parser.add_argument("--repo", type=str, default=TARGET_REPO,
                        help=f"Target repository in 'owner/repo' format (default: {TARGET_REPO})")
    parser.add_argument("--days", type=int, default=DAYS_ACTIVE,
                        help=f"Number of days to look back for activity (default: {DAYS_ACTIVE})")
    parser.add_argument("--token", type=str, default=os.getenv("GITHUB_TOKEN"),
                        help="GitHub API token (can also be set via GITHUB_TOKEN environment variable)")

    args = parser.parse_args()

    TARGET_REPO = args.repo
    DAYS_ACTIVE = args.days
    GITHUB_TOKEN = args.token

    print(f"Starting PR activity report for {TARGET_REPO} covering the last {DAYS_ACTIVE} days.")

    # Step 2: Fetch all open pull requests
    # DAYS_ACTIVE is used by placeholder functions for now, not directly by get_pull_requests for fetching.
    open_pull_requests = get_pull_requests(TARGET_REPO, GITHUB_TOKEN)

    if open_pull_requests is None:
        print("Failed to retrieve pull requests. Exiting.")
        exit()

    print(f"Fetched {len(open_pull_requests)} open pull requests. Now filtering by overall activity...")

    active_prs_details = [] # Will store PRs that pass the activity filter

    # Define since_date for activity checking, ensure it's offset-aware (UTC)
    since_date_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DAYS_ACTIVE)

    for pr_data in open_pull_requests:
        pr_updated_at_str = pr_data.get('updated_at')
        pr_updated_at_dt = None
        if pr_updated_at_str:
            # Convert GitHub's ISO8601 string to offset-aware datetime object
            pr_updated_at_dt = datetime.datetime.fromisoformat(pr_updated_at_str.replace('Z', '+00:00'))

        is_pr_itself_recent = pr_updated_at_dt and pr_updated_at_dt > since_date_dt

        # These calls will be replaced by actual data fetching in later steps
        recent_comments = get_recent_comments(pr_data['number'], TARGET_REPO, GITHUB_TOKEN, DAYS_ACTIVE)
        recent_commits = get_recent_commits(pr_data['number'], TARGET_REPO, GITHUB_TOKEN, DAYS_ACTIVE)

        if is_pr_itself_recent or recent_comments or recent_commits:
            # Store the PR and its activity details for report generation
            pr_data['fetched_comments'] = recent_comments # Store for later use by process_pr_data/generate_report
            pr_data['fetched_commits'] = recent_commits   # Store for later use
            active_prs_details.append(pr_data)
            # print(f"PR #{pr_data['number']} is active.") # Optional: for debugging
        # else:
            # print(f"PR #{pr_data['number']} is not active in the last {DAYS_ACTIVE} days.") # Optional

    print(f"Found {len(active_prs_details)} pull requests with overall activity in the last {DAYS_ACTIVE} days.")

    if active_prs_details:
        # process_pr_data now receives PRs that are confirmed active and may include 'fetched_comments'/'fetched_commits'
        processed_active_prs = process_pr_data(active_prs_details, TARGET_REPO)

        if processed_active_prs:
            print(f"Successfully processed {len(processed_active_prs)} active PRs.")
            # generate_report will use the processed data, including summaries of comments/commits
            report = generate_report(processed_active_prs, TARGET_REPO, DAYS_ACTIVE)
            print("\n" + report)
        else:
            print("No active PRs were processed (e.g., if process_pr_data filtered them all out or failed).")
    else:
        print("No PRs found with overall activity in the specified period.")
    # Future function calls will go here, e.g. for saving report to file
