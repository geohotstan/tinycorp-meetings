import os
import json
import argparse
from github import Github
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv() # Load .env file for GITHUB_TOKEN, REPO_NAME etc.

def parse_datetime_utc_arg(dt_str):
    """
    Parses a datetime string for argparse.
    This function is intended to be used as the 'type' for an argparse argument.
    It will be called by argparse for --start and --end individually.
    For more complex logic like setting end of day, we'll adjust the parsed datetime later.
    """
    # Common logic from the original parse_datetime_utc
    parsed_dt_str = dt_str
    if dt_str.endswith('Z'):
        # Python's fromisoformat handles 'Z' correctly in >=3.11
        # For broader compatibility, can replace 'Z' with '+00:00'
        # parsed_dt_str = dt_str[:-1] + '+00:00'
        pass # fromisoformat should handle Z

    try:
        dt = datetime.fromisoformat(parsed_dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except ValueError:
        try:
            # Try parsing just date YYYY-MM-DD, treat as start of day UTC
            d_obj = datetime.strptime(dt_str, "%Y-%m-%d").date()
            return datetime(d_obj.year, d_obj.month, d_obj.day, 0, 0, 0, tzinfo=timezone.utc)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid datetime format '{dt_str}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ.")

def adjust_end_datetime(dt):
    """Adjusts a datetime to be the end of its day if only date was specified."""
    # If time is 00:00:00, assume it was a date-only input and adjust to end of day
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt

def ensure_utc(dt):
    """Ensure datetime object is timezone-aware and in UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch GitHub repository activity within a specified time range and output as JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
    )

    # Default values for start and end dates
    default_start_dt = (datetime.now(timezone.utc) - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    default_end_dt = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)

    parser.add_argument(
        "--repo",
        type=str,
        default="geohot/tinygrad",
        help="Target repository in 'owner/repository' format. "
             "Can also be set via REPO_NAME environment variable."
    )
    parser.add_argument(
        "--start",
        type=parse_datetime_utc_arg,
        default=default_start_dt,
        help="Start datetime for the report (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ). "
             "If only date is given, time defaults to 00:00:00 UTC. "
             "Can also be set via START_DATETIME environment variable."
    )
    parser.add_argument(
        "--end",
        type=parse_datetime_utc_arg,
        default=default_end_dt,
        help="End datetime for the report (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ). "
             "If only date is given, time defaults to 23:59:59 UTC for that day. "
             "Can also be set via END_DATETIME environment variable."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path for the JSON report. If not specified, prints to stdout."
    )

    args = parser.parse_args()

    # --- Configuration from args ---
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    REPO_NAME = args.repo

    # Parse datetime strings from env vars if args used env var strings
    if isinstance(args.start, str): # Means it came from os.environ.get() and wasn't parsed by argparse type
        report_start_dt = parse_datetime_utc_arg(args.start)
    else: # Parsed by argparse 'type'
        report_start_dt = args.start

    if isinstance(args.end, str):
        report_end_dt = parse_datetime_utc_arg(args.end)
    else:
        report_end_dt = args.end

    # Adjust end_dt to be end of day if it was specified as date-only
    report_end_dt = adjust_end_datetime(report_end_dt)

    OUTPUT_FILE = args.output
    # --- End Configuration ---

    if not GITHUB_TOKEN:
        parser.error("GITHUB_TOKEN not found. Set it via --token argument or GITHUB_TOKEN environment variable. "
                     "Please create a Personal Access Token (PAT) with 'repo' scope.")

    try:
        g = Github(GITHUB_TOKEN)
    except Exception as e:
        print(f"Error initializing GitHub client: {e}", file=os.sys.stderr)
        exit(1)

    try:
        repo = g.get_repo(REPO_NAME)
    except Exception as e:
        print(f"Error: Could not get repository '{REPO_NAME}'. Check PAT permissions and repo name. Exception: {e}", file=os.sys.stderr)
        exit(1)

    if report_start_dt >= report_end_dt:
        print("Error: Start datetime must be before end datetime.", file=os.sys.stderr)
        exit(1)

    print(f"Fetching activity for {REPO_NAME} from {report_start_dt.isoformat()} to {report_end_dt.isoformat()}", file=os.sys.stderr)

    all_activity_by_date = {}

    search_range_str = f"{report_start_dt.isoformat()}..{report_end_dt.isoformat()}"

    # 1. Merged PRs
    print("Fetching merged PRs...", file=os.sys.stderr)
    merged_prs_all_period = []
    query_merged = f"repo:{REPO_NAME} is:pr is:merged merged:{search_range_str}"
    try:
        for pr_item in g.search_issues(query=query_merged, sort="updated", order="desc"):
            pr = repo.get_pull(pr_item.number)
            merged_at_utc = ensure_utc(pr.merged_at)
            if merged_at_utc and report_start_dt <= merged_at_utc <= report_end_dt:
                merged_prs_all_period.append({
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "author": pr.user.login,
                    "merged_by": pr.merged_by.login if pr.merged_by else "unknown",
                    "merged_at": merged_at_utc.isoformat(),
                    "activity_date": merged_at_utc.date()
                })
    except Exception as e:
        print(f"Warning: Could not fetch merged PRs. Error: {e}", file=os.sys.stderr)

    # 2. New Issues (excluding PRs)
    print("Fetching new issues...", file=os.sys.stderr)
    new_issues_all_period = []
    query_issues = f"repo:{REPO_NAME} is:issue type:issue created:{search_range_str}"
    try:
        for issue in g.search_issues(query=query_issues, sort="created", order="asc"):
            created_at_utc = ensure_utc(issue.created_at)
            if report_start_dt <= created_at_utc <= report_end_dt:
                new_issues_all_period.append({
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "author": issue.user.login,
                    "created_at": created_at_utc.isoformat(),
                    "activity_date": created_at_utc.date()
                })
    except Exception as e:
        print(f"Warning: Could not fetch new issues. Error: {e}", file=os.sys.stderr)

    # 3. New PRs
    print("Fetching new PRs...", file=os.sys.stderr)
    new_prs_all_period = []
    query_new_prs = f"repo:{REPO_NAME} is:pr type:pr created:{search_range_str}"
    try:
        for pr_item in g.search_issues(query=query_new_prs, sort="created", order="asc"):
            created_at_utc = ensure_utc(pr_item.created_at)
            if report_start_dt <= created_at_utc <= report_end_dt:
                new_prs_all_period.append({
                    "number": pr_item.number,
                    "title": pr_item.title,
                    "url": pr_item.html_url,
                    "author": pr_item.user.login,
                    "created_at": created_at_utc.isoformat(),
                    "activity_date": created_at_utc.date()
                })
    except Exception as e:
        print(f"Warning: Could not fetch new PRs. Error: {e}", file=os.sys.stderr)

    # 4. Reopened PRs (from Events API)
    print("Fetching events for reopened PRs (may take time for long ranges or active repos)...", file=os.sys.stderr)
    reopened_prs_all_period = []
    try:
        for event in repo.get_events():
            event_created_at_utc = ensure_utc(event.created_at)
            if event_created_at_utc < report_start_dt:
                break
            if event_created_at_utc > report_end_dt:
                continue
            if event.type == 'PullRequestEvent' and event.payload.get('action') == 'reopened':
                pr_payload = event.payload['pull_request']
                original_author = pr_payload['user']['login'] if pr_payload.get('user') else "unknown"
                reopened_prs_all_period.append({
                    "number": pr_payload['number'],
                    "title": pr_payload['title'],
                    "url": pr_payload['html_url'],
                    "original_author": original_author,
                    "reopened_by": event.actor.login,
                    "reopened_at": event_created_at_utc.isoformat(),
                    "activity_date": event_created_at_utc.date()
                })
    except Exception as e:
        print(f"Warning: Could not fetch events for reopened PRs. Error: {e}", file=os.sys.stderr)

    # --- Iterate through dates in the report range and populate all_activity_by_date ---
    current_processing_date = report_start_dt.date()
    final_report_date = report_end_dt.date()

    while current_processing_date <= final_report_date:
        date_str = current_processing_date.isoformat()
        daily_activity = {
            "merged_prs": [],
            "new_issues": [],
            "new_prs": [],
            "reopened_prs": []
        }

        for pr_data in merged_prs_all_period:
            if pr_data["activity_date"] == current_processing_date:
                daily_activity["merged_prs"].append({k: v for k, v in pr_data.items() if k != "activity_date"})
        for issue_data in new_issues_all_period:
            if issue_data["activity_date"] == current_processing_date:
                daily_activity["new_issues"].append({k: v for k, v in issue_data.items() if k != "activity_date"})
        for pr_data in new_prs_all_period:
            if pr_data["activity_date"] == current_processing_date:
                daily_activity["new_prs"].append({k: v for k, v in pr_data.items() if k != "activity_date"})
        for pr_data in reopened_prs_all_period:
            if pr_data["activity_date"] == current_processing_date:
                daily_activity["reopened_prs"].append({k: v for k, v in pr_data.items() if k != "activity_date"})

        for category_key in daily_activity:
            daily_activity[category_key].sort(key=lambda x: x.get("number", 0))

        is_empty_day = all(not daily_activity[cat] for cat in daily_activity)
        if is_empty_day:
            daily_activity["message"] = "No notable activity found for this day."

        all_activity_by_date[date_str] = daily_activity
        current_processing_date += timedelta(days=1)

    # Output JSON
    if OUTPUT_FILE:
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_activity_by_date, f, indent=2, ensure_ascii=False)
            print(f"\nSuccessfully generated report and saved to {OUTPUT_FILE}", file=os.sys.stderr)
        except IOError as e:
            print(f"\nError writing to output file {OUTPUT_FILE}: {e}", file=os.sys.stderr)
            print("Report JSON (fallback to stdout):", file=os.sys.stderr)
            print(json.dumps(all_activity_by_date, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(all_activity_by_date, indent=2, ensure_ascii=False))
        print(f"\nSuccessfully generated report for {REPO_NAME}.", file=os.sys.stderr)

if __name__ == "__main__":
    main()