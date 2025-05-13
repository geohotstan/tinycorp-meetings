import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
import sys
from pathlib import Path

def upload_video(file, title, description, category="22", privacy="public"):
    # Set up YouTube API client
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    client_secrets_file = str(Path(__file__).parent.parent.parent.joinpath("client_secrets.json"))

    # Authenticate
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    # Configure video upload
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy
        }
    }
    media_file = MediaFileUpload(file, chunksize=-1, resumable=True)

    # Make the API request to upload
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()
    return f"https://www.youtube.com/watch?v={response['id']}"

if __name__ == "__main__":
    assert len(sys.argv) == 2
    date, extension = sys.argv[1].split('.')
    assert extension == "mp4"
    url = upload_video(f"{date}.mp4", f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/')
    print(url)
