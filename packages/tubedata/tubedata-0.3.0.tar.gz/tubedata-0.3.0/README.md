# TubeData

[![PyPI version](https://badge.fury.io/py/tubedata.svg)](https://badge.fury.io/py/tubedata)

Make YouTube queries and get information from videos (including captions, likes, titles, etc.) ready for Jupyter Notebooks.

## Installation

```shell
pip install tubedata
```

## USAGE

Create a search object

```python
import tubedata as yt
tubedata_search = yt.Search("Test", developer_key=<YOUR_YOUTUBE_DEVELOPER_KEY>)
tubedata_search.df  # DataFrame with YouTube infos (likes, views, title, etc.)
```

__Output example:__

| videoId   | publishedAt               | channelId    | title                 | … | viewCount | likeCount | favoriteCount | commentCount |
|-----------|---------------------------|--------------|-----------------------|---|-----------|-----------|---------------|--------------|
| abcde1234 | 2021-06-01 10:00:00+00:00 | abcde1234abc | Video title example 1 | … | 100000    | 6000      | 0             | 200          |
| abcde1235 | 2021-06-01 11:00:00+00:00 | abcde1234abc | Video title example 2 | … | 200000    | 5000      | 1             | 210          |
| abcde1236 | 2021-06-01 12:00:00+00:00 | abcde1234abd | Video title example 3 | … | 100000    | 4000      | 0             | 150          |
| …         | …                         | …            | …                     | … | …         | …         | …             | …            |

### Developer key

To use ```tubedata``` a Google YouTube developer key needs to be created following https://developers.google.com/youtube/registering_an_application?hl=en and can be set as environment variable.

### Developer key as environment variable

**Linux**: edit ~/.profile and add as last line of code:

```bash
export YOUTUBE_DEVELOPER_KEY=<YOUR_YOUTUBE_DEVELOPER_KEY>
```

### Captions

To get captions, use the argument ```captions=True```

```python
import tubedata as yt
# YOUTUBE_DEVELOPER_KEY is not necessary if was set as environment variable
tubedata_search = yt.Search("Test", caption=True)
tubedata_search.df  # A new column with captions "video_caption" will appear
```

__Output example:__

| videoId   | publishedAt               | channelId    | title                 | … | commentCount | video_caption                                            |
|-----------|---------------------------|--------------|-----------------------|---|--------------|----------------------------------------------------------|
| abcde1234 | 2021-06-01 10:00:00+00:00 | abcde1234abc | Video title example 1 | … | 200          | What they say; words and more words; thanks for watching |
| abcde1235 | 2021-06-01 11:00:00+00:00 | abcde1234abc | Video title example 2 | … | 210          | None                                                     |
| abcde1236 | 2021-06-01 12:00:00+00:00 | abcde1234abd | Video title example 3 | … | 150          | Words and more words and more words; thanks for watching |
| …         | …                         | …            | …                     | … | …            | …                                                        |

### Channel Dataframes

To get information about channels instead of videos, use the argument `item_type="channel"`:

```python
import tubedata as yt
# Search for channels instead of videos
tubedata_search = yt.Search("Test", item_type="channel")
tubedata_search.df  # DataFrame with YouTube channel information
```

__Output example:__

| channelId    | publishedAt               | title                  | description                      | channelTitle         | publishTime                |
|--------------|---------------------------|------------------------|----------------------------------|----------------------|----------------------------|
| abcde1234abc | 2021-06-01 10:00:00+00:00 | Example channel 1      | Description of example channel 1 | Example channel 1    | 2021-06-01 10:00:00+00:00 |
| abcde1234abd | 2021-06-01 11:00:00+00:00 | Example channel 2      | Description of example channel 2 | Example channel 2    | 2021-06-01 11:00:00+00:00 |
| …            | …                         | …                      | …                                | …                    | …                          |

### Channel Information

To get information and captions from videos of specific channel(s), use the `ChannelInfo` class:

```python
import tubedata as yt
# Get information from videos of specific channel(s)
channel_info = yt.ChannelInfo(
    channel_ids=["UCWDeEIDAIi_oYKDiqwfGyRg"],  # Channel ID or list of IDs
    max_results=10,  # Maximum number of results per channel
    accepted_caption_lang=['pt', 'en'],  # Accepted languages for captions
    developer_key="YOUR_DEVELOPER_KEY"  # Optional if set as environment variable
)
channel_info.df  # DataFrame with video information and captions
```

__Output example:__

| channelId           | videoId     | title                 | publishedAt               | caption                                                 | thumbnailUrl                    |
|---------------------|-------------|------------------------|---------------------------|--------------------------------------------------------|----------------------------------|
| UCWDeEIDAIi_oYKDiqw | v42YdTRXStU | Coca-Cola Advertising | 2025-03-22 22:00:39+00:00 | Hello everyone; In this video we will talk about; Thanks... | https://i.ytimg.com/vi/sddefault.jpg |
| UCWDeEIDAIi_oYKDiqw | cm9ecYbFZFE | Be careful with people| 2025-03-22 18:00:22+00:00 | Be careful with people; that you follow on social media... | https://i.ytimg.com/vi/maxresdefault.jpg |
| …                   | …           | …                     | …                         | …                                                      | …                                |

## Available Arguments

The `Search` class accepts the following arguments:

- `term`: YouTube search term (required)
- `caption`: If `True`, includes video captions (default: `False`)
- `maxres`: Maximum number of results to return (default: `50`)
- `accepted_caption_lang`: List of accepted languages for captions (default: `['en']`)
- `item_type`: Type of item to search for: "video" or "channel" (default: "video")
- `developer_key`: YouTube API developer key (optional if set as environment variable)

Example using all arguments:

```python
import tubedata as yt

tubedata_search = yt.Search(
    term="Python Tutorial",
    caption=True,
    maxres=100,
    accepted_caption_lang=['pt', 'en'],
    item_type="video",
    developer_key="YOUR_DEVELOPER_KEY"
)

# Access the resulting DataFrame
df = tubedata_search.df
```

The `ChannelInfo` class accepts the following arguments:

- `channel_ids`: Channel ID or list of channel IDs (required)
- `max_results`: Maximum number of results per channel (default: `10`)
- `accepted_caption_lang`: List of accepted languages for captions (default: `['pt', 'en']`)
- `developer_key`: YouTube API developer key (optional if set as environment variable)

Example using all arguments:

```python
import tubedata as yt

channel_info = yt.ChannelInfo(
    channel_ids=["UCWDeEIDAIi_oYKDiqwfGyRg", "UC_x5XG1OV2P6uZZ5FSM9Ttw"],
    max_results=20,
    accepted_caption_lang=['pt', 'en', 'es'],
    developer_key="YOUR_DEVELOPER_KEY"
)

# Access the resulting DataFrame
df = channel_info.df
```
