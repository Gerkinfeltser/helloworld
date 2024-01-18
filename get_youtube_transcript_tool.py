import sys
from langchain.tools import tool
from pytube import YouTube # for video title
import re
from youtube_transcript_api import YouTubeTranscriptApi

show_raw_transcript=True
output_as_file=True
delimiter="; "  # Choose a unique delimiter
output_file_name='transcript_output.txt'

# Tool for grabbing a YouTube title from the provided url
@tool
def get_youtube_video_title(video_url):
    """
    Grabs a specified youtube video's title.

    :param video_url: URL of the YouTube video.
    :return: The title
    """
    yt = YouTube(video_url)
    return yt.title

# Tool for extracting YouTube transcript segments
@tool
def get_youtube_transcript_segments(video_url: str) -> list:
    """
    Extracts and splits the transcript from a given YouTube video URL into manageable segments.

    :param video_url: URL of the YouTube video.
    :return: A list of transcript segments.
    """
    # Extract the video ID from the URL
    video_id = re.search(r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)", video_url)
    if not video_id:
        return ["Unable to extract video ID from the URL."]
    video_id = video_id.group(0)

    # Fetch the transcript of the video
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        return [str(e)]

    # Remove all instances of "[Music]" and combine the text of the transcript into a single string
    full_transcript = ' '.join([entry['text'].replace("[Music]", "") for entry in transcript_list])


    # Split transcript into segments using the nearest space approach
    segment_length = 800  # Adjust the segment length: Experiment with this number to find a balance
    segments = split_transcript_at_nearest_space(full_transcript, segment_length)

    # Use a unique delimiter to join segments into a single string
    task_description = delimiter.join(segments)

    return task_description

def split_transcript_at_nearest_space(full_transcript, max_segment_length):
    """
    Splits the transcript into segments, trying to avoid cutting off in the middle of a word.

    :param full_transcript: The complete transcript as a single string.
    :param max_segment_length: Maximum character length for each segment.
    :return: A list of transcript segments.
    """
    segments = []
    while len(full_transcript) > max_segment_length:
        # Find the nearest space before the max_segment_length
        split_index = full_transcript.rfind(' ', 0, max_segment_length)
        
        # If no space is found, default to the max length
        if split_index == -1:
            split_index = max_segment_length

        # Split the transcript and add the segment
        segment = full_transcript[:split_index].strip()
        segments.append(segment)
        
        # Remove the processed part from the transcript
        full_transcript = full_transcript[split_index:].lstrip()

    # Add the remaining part of the transcript
    if full_transcript:
        segments.append(full_transcript.strip())

    return segments

# Main Flow
# User Input (YouTube Video URL)
video_title = ''
default_url = 'https://www.youtube.com/watch?v=Lty7RAHKT9E'

if len(sys.argv) > 1:
    user_input_url = sys.argv[1]
else:
    user_input_url = input(">>> Please enter the YouTube video URL: ")
    if not user_input_url:
        user_input_url = default_url
        print('>>> Paging Dr. Steve...')
    else:
        print(f'Grabbing transcript for {video_title}')

video_title = get_youtube_video_title(user_input_url)
transcript_segments = get_youtube_transcript_segments(user_input_url)

# Raw Transcript Print setup for Debugging/Clarity
if show_raw_transcript:
    raw_transcript_header = f'>>>>>>>>>>>>>>>>>>\n>>>>>> RAW [{video_title}] TRANSCRIPT START >>>>>>:\n'
    raw_transcript_footer = f'\n\n<<<<<< RAW [{video_title}] TRANSCRIPT END <<<<<<\n<<<<<<<<<<<<<<<<<<'
    print(raw_transcript_header)
    for segment in transcript_segments:
        print(segment, end="")
    print(raw_transcript_footer)
    
# Open a file in write mode
if output_as_file:
    with open(output_file_name, 'w') as file:
        file.write(video_title+"\n\n")
        for segment in transcript_segments:
            file.write(segment)
    print(f'{output_file_name} written!')
