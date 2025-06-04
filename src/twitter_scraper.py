import snscrape.modules.twitter as sntwitter
# import csv # No longer needed
import argparse
import json # Added for JSON output
    """
    Scrapes tweets for a given keyword.

    Args:
        keyword (str): The keyword to search for.
        max_tweets (int): The maximum number of tweets to scrape.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              the URL, date, content, and username of a tweet.
    """
    tweets_list = []
    try:
        scraper = sntwitter.TwitterSearchScraper(keyword)
        for i, tweet in enumerate(scraper.get_items()):
            if i >= max_tweets:
                break
            tweet_details = {
                'url': tweet.url,
                'date': tweet.date.isoformat(),
                'content': tweet.rawContent,  # or tweet.renderedContent
                'username': tweet.user.username,
                'like_count': tweet.likeCount if hasattr(tweet, 'likeCount') else 0,
                'retweet_count': tweet.retweetCount if hasattr(tweet, 'retweetCount') else 0,
                'reply_count': tweet.replyCount if hasattr(tweet, 'replyCount') else 0,
                'quote_count': tweet.quoteCount if hasattr(tweet, 'quoteCount') else 0,
            }
            tweet_details['popularity_score'] = (
                tweet_details.get('like_count', 0) +
                tweet_details.get('retweet_count', 0) +
                tweet_details.get('reply_count', 0) +
                tweet_details.get('quote_count', 0)
            )
            tweets_list.append(tweet_details)
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return []  # Return empty list on error
    return tweets_list

# def save_to_csv(data, filename):
#     """
#     Saves a list of tweet data to a CSV file.
#
#     Args:
#         data (list): A list of dictionaries, where each dictionary contains tweet data.
#         filename (str): The name of the CSV file to save.
#     """
#     try:
#         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#             if not data:
#                 print("No data to save.")
#                 return
#
#             # Define a consistent order for CSV headers
#             fieldnames = [
#                 'Username', 'Date', 'URL', 'Content',
#                 'like_count', 'retweet_count', 'reply_count', 'quote_count',
#                 'popularity_score'
#             ]
#
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             for tweet_row in data:
#                 # Ensure all rows have all fieldnames, fill with default (e.g. empty string or 0) if missing
#                 row_to_write = {field: tweet_row.get(field, '') for field in fieldnames}
#                 writer.writerow(row_to_write)
#         print("Data saved successfully.")
#     except IOError as e:
#         print(f"An I/O error occurred while writing to {filename}: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred while writing to {filename}: {e}")

def save_to_json(data, filename):
    """
    Saves a list of tweet data to a JSON file.

    Args:
        data (list): A list of dictionaries, where each dictionary contains tweet data.
        filename (str): The name of the JSON file to save.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved successfully to {filename}")
    except IOError as e:
        print(f"An I/O error occurred while writing to {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing to {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape tweets from Twitter based on a keyword.")
    parser.add_argument("keyword", help="The keyword to search for on Twitter.")
    parser.add_argument(
        "--max_tweets",
        type=int,
        default=100,
        help="Maximum number of tweets to scrape. Default is 100."
    )
    parser.add_argument(
        "--output_file",
        dest="output_filename", # Changed destination variable name for clarity
        help="Name of the JSON file to save tweets to. Defaults to '{keyword}_tweets.json'."
    )

    args = parser.parse_args()

    keyword_to_search = args.keyword
    number_of_tweets_to_scrape = args.max_tweets

    # Determine output filename
    if args.output_filename:
        # If user provides a filename, use it. Ensure it ends with .json
        if not args.output_filename.lower().endswith(".json"):
            output_json_file = f"{args.output_filename}.json"
        else:
            output_json_file = args.output_filename
    else:
        # Default filename if not provided by user
        output_json_file = f"{keyword_to_search}_tweets.json"

    print(f"Scraping tweets for '{keyword_to_search}'...")
    tweet_data = scrape_tweets(keyword_to_search, number_of_tweets_to_scrape)

    if tweet_data: # Check if list is not empty (i.e. scraping was successful and found tweets)
        print(f"Successfully scraped {len(tweet_data)} tweets.")

        # Sort tweets by popularity_score in descending order
        tweet_data.sort(key=lambda tweet: tweet.get('popularity_score', 0), reverse=True)
        print("Tweets sorted by popularity score.")

        print(f"Saving data to {output_json_file}...")
        save_to_json(tweet_data, output_json_file) # Use the new JSON saver

        # Optional: Print a few tweets to console for quick check, if data was scraped
        if tweet_data: # Redundant check if scrape_tweets returns [] on error, but good for clarity
            for i, tweet in enumerate(tweet_data[:3]): # Print first 3
                print(f"--- Tweet {i+1} ---")
                print(f"User: {tweet['username']}, Date: {tweet['date']}, URL: {tweet['url']}")
                print(f"Content: {tweet['content'][:100]}...")
    elif not tweet_data and keyword_to_search: # Handles case where scraping might have failed and returned []
        print(f"No tweets found for '{keyword_to_search}', or an error occurred during scraping.")
    else: # Should not happen if keyword is always provided by argparse
        print("No keyword provided for scraping.")
