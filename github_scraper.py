import datetime
import json # Not strictly necessary for this script, but good practice

try:
    import requests
except ImportError:
    print("The 'requests' library is required. Please install it by running: pip install requests")
    exit()

def main():
    # Calculate the date for 7 days ago
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)
    formatted_date = seven_days_ago.strftime('%Y-%m-%d')

    # Construct the GitHub API query URL
    base_url = "https://api.github.com/search/repositories"
    query_params = {
        'q': f'tinygrad pushed:>{formatted_date}',
        'sort': 'updated',
        'order': 'desc'
    }

    # Construct the full URL with parameters
    query_string = '&'.join([f"{key}={value}" for key, value in query_params.items()])
    api_url = f"{base_url}?{query_string}"

    # Fetch data from the API
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Process the response
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                project_name = item.get('name')
                project_url = item.get('html_url')
                description = item.get('description') if item.get('description') else "No description available."
                last_pushed = item.get('pushed_at')

                print(f"Project Name: {project_name}")
                print(f"Project URL: {project_url}")
                print(f"Description: {description}")
                print(f"Last Pushed: {last_pushed}")
                print("---")
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
