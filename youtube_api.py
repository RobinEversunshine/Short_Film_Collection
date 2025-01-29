from googleapiclient.discovery import build
import re



# Your YouTube Data API key
API_KEY = "AIzaSyDqaTahki6YXkGK-gm0JFMNyUDIFNS4aus"



# Function to extract video ID from a YouTube URL
def extractYoutubeId(url : str):
    match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
    if match:
        print(match.group())
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")



# Function to fetch video details
def getYoutubeInfor(video_url : str):
    # Extract video ID
    video_id = extractYoutubeId(video_url)

    # Initialize the YouTube API client
    youtube = build("youtube", "v3", developerKey=API_KEY)

    # Fetch video details
    response = youtube.videos().list(
        part="snippet,contentDetails",
        id=video_id
    ).execute()

    # Extract details from the API response
    if "items" in response and response["items"]:
        video_data = response["items"][0]["snippet"]


        #get video duration
        duration_iso = response["items"][0]["contentDetails"]["duration"]

        match = re.search(r"(\d+)M(\d+)S", duration_iso)
        if match:
            duration = int(match.group(1)) + round(float(match.group(2)) / 60.0)
        else:
            duration = 0


        # for name, value in video_data.items():
        #     print(f"{name} : {value}\n")

        if "maxres" in video_data["thumbnails"]:
            image_url = video_data["thumbnails"]["maxres"]["url"]
        elif "standard" in video_data["thumbnails"]:
            image_url = video_data["thumbnails"]["standard"]["url"]
        elif "high" in video_data["thumbnails"]:
            image_url = video_data["thumbnails"]["high"]["url"]
        elif "medium" in video_data["thumbnails"]:
            image_url = video_data["thumbnails"]["medium"]["url"]
        else:
            image_url = video_data["thumbnails"]["default"]["url"]


        #return items
        return {
            "title": video_data["title"],
            "description": video_data["description"],
            "release_date": video_data["publishedAt"][:10],
            "uploader": video_data["channelTitle"],
            "image_url": image_url,
            "url": f"youtube.com/watch?v={video_id}",
            #"language" : video_data["defaultAudioLanguage"],
            "duration" : duration
        }
    else:
        print(f"No video found for the given ID youtube.com/watch?v={video_id}")


#getYoutubeInfor("https://www.youtube.com/watch?v=31SVPJCsMtM&list=PLDD1-_y9Cq_0bMSlaPdWdxh0SZyH_ULHa&index=5")
# # Example usage
# video_url = "https://www.youtube.com/watch?v=X0_JILE6JbA&list=PLDD1-_y9Cq_0bMSlaPdWdxh0SZyH_ULHa&index=19"
# try:
#     video_details = getYoutubeInfor(video_url)
#     # print("Title:", video_details["title"])
#     # print("Description:", video_details["description"])
#     # print("Upload Time:", video_details["upload_time"])
#     # print("Uploader:", video_details["uploader"])
# except Exception as e:
#     print("Error:", e)
