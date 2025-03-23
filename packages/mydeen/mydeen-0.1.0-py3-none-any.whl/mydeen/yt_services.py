from typing import Any, NamedTuple, List, Dict, TypedDict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .config import Config


class Channels(NamedTuple):
    lislamsimplement: str
    larabesimplement: str
    lecoransimplement: str


class Playlist(TypedDict):
    title: str
    id: str
    video_count: int
    thumbnail: str
    url_playlist: str
    description: str


class Video(TypedDict):
    title: str
    video_id: str
    position: int
    published_at: str
    thumbnail: str
    url: str


class YoutubeServices:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.youtube: Any = build(
            "youtube", "v3", developerKey=api_key, cache_discovery=False
        )
        self.handles = Config.handles_yt()
        self.channels = self.__connect_id_channels()

    def __connect_id_channels(self) -> Channels:
        """
        Récupère les identifiants des chaînes Youtube à partir de leur handle.
        """
        channels = {}
        for k, v in self.handles._asdict().items():
            channels[k] = self.get_channel_id(v)
        return Channels(**channels)

    def get_channel_id(self, handle: str) -> str:
        """
        Récupère l'identifiant d'une chaîne Youtube à partir de son handle (ex: @lecoransimplement).
        """
        try:
            req = self.youtube.search().list(
                part="snippet", type="channel", q=handle, maxResults=1
            )
            res = req.execute()
            if res["items"]:
                return res["items"][0]["snippet"]["channelId"]
            return None
        except HttpError as e:
            raise e

    def get_playlist(self, channel_id: str) -> List[Playlist]:
        """
        Récupère la liste des playlists d'une chaîne Youtube.
        """
        playlists = []
        next_page_token = None
        while True:
            req = self.youtube.playlists().list(
                part="snippet, contentDetails",
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            res = req.execute()
            playlists.extend(res["items"])
            next_page_token = res.get("nextPageToken")
            if not next_page_token:
                break
        return self.__parser_playlist(playlists)

    def __parser_playlist(self, playlists: List[Dict[str, Any]]) -> List[Playlist]:
        """
        Parse les playlists pour récupérer les informations nécessaires.
        """
        data = []
        for playlist in playlists:
            data.append(
                {
                    "title": playlist["snippet"]["title"],
                    "id": playlist["id"],
                    "video_count": playlist["contentDetails"]["itemCount"],
                    "thumbnail": playlist["snippet"]["thumbnails"]
                    .get("medium", {})
                    .get("url"),
                    "url_playlist": f"https://www.youtube.com/playlist?list={playlist['id']}",
                    "description": playlist["snippet"].get("description", ""),
                }
            )
        return data

    def get_videos_playlist(self, playlist_id: str) -> List[Video]:
        """
        Récupère les vidéos d'une playlist.
        """
        videos = []
        next_page_token = None
        while True:
            req = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            res = req.execute()
            videos.extend(res["items"])
            next_page_token = res.get("nextPageToken")
            if not next_page_token:
                break
        return self.__parser_videos(videos, playlist_id)

    def __parser_videos(
        self, videos: List[Dict[str, Any]], playlist_id: str
    ) -> List[Video]:
        """
        Parse les vidéos pour récupérer les informations nécessaires.
        """
        data = []
        for video in videos:
            video_id = video["snippet"]["resourceId"]["videoId"]
            data.append(
                {
                    "title": video["snippet"]["title"],
                    "video_id": video_id,
                    "position": video["snippet"]["position"],
                    "published_at": video["snippet"]["publishedAt"],
                    "thumbnail": video["snippet"]["thumbnails"]
                    .get("medium", {})
                    .get("url"),
                    "url": f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}",
                }
            )
        return data
