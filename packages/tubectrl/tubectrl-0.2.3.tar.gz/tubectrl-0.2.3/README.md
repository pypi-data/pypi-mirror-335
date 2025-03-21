# TubeCtrl

## Overview

A python library that wraps around the YouTube V3 API. You can use it find and manage YouTube resources including Videos, Playlists, Channels and Comments.

The library is modelled after [Google's own documentation](https://developers.google.com/youtube/v3/docs/videos).

## Requirements

- Python 3.10+
- Works on Linux, Windows, macOS, BSD

## Installation

```sh
pip install tubectrl
```

## Get started

To get started, you need a verified Google Account and Google API keys with the correct permissions.

### How to Get A Google API Key

Follow the instructions in this short [article](https://medium.com/@lyle-okoth/how-to-get-a-google-api-key-d3c38649eaae) to get an API key.

To get a particular video using the videos' id:

1. Create an instance of the YouTube API passing in the path to the downloaded client secret file:

```sh
from tubectrl import YouTube

client_secrets_file = '/home/lyle/Downloads/secrets.json'
youtube = YouTube(client_secrets_file)
youtube.authenticate()
```

2. Use the video id to find the video:

```python
video = youtube.find_video_by_id('rfscVS0vtbw')
```

3. To find many videos using their id's:

```python
ids = ['rfscVS0vtbw', 'TFa38ONq5PY']
videos = youtube.find_videos(ids)
```

4. To find the most popular videos in a given region e.g Kenya, pass in the region code:

```python
popular_kenyan_videos = youtube.find_most_popular_video_by_region('ke')
```

5. To search for videos (this returns an iterator):

```python
from youtube.schemas import (
    SearchFilter, SearchOptionalParameters, SearchPart, YouTubeResponse, YouTubeRequest
)
from typing import Iterator
from youtube.models import Video

query: str = 'Python programming videos'
max_results: int = 10
part: SearchPart = SearchPart()
optional_parameters: SearchOptionalParameters = SearchOptionalParameters(
    q=query,
    maxResults=max_results,
    type=['video', 'playlist', 'channel']
)
search_request: YouTubeRequest = YouTubeRequest(
    part=part,
    optional_parameters=optional_parameters
)
video_iterator: Iterator = youtube.get_search_iterator(search_request)
videos: list[Video] = next(video_iterator)
```

## Documentation and Tutorials

To learn more about the library including the documentation and tutorials, check out the [libraries' documentation](https://youtube-wrapper.readthedocs.io/en/latest/).

## How to Contribute

To contribute, chack out the [contribution guideline](CONTRIBUTING.md).

## License

The API uses an [MIT License](LICENSE)

## Developer

Lyle Okoth – [@lylethedesigner](https://twitter.com/lylethokoth) on twitter

[lyle okoth](https://medium.com/@lyle-okoth) on medium

My email is <lyceokoth@gmail.com>

Here is my [GitHub Profile](https://github.com/twyle/)

You can also find me on [Linkedin](https://www.linkedin.com/in/lyle-okoth/)
