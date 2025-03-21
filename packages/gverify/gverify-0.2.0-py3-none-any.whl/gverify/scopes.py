from enum import Enum


class YouTubeScopes(Enum):
    youtube_force_ssl = "https://www.googleapis.com/auth/youtube.force-ssl"
    youtube_readonly = "https://www.googleapis.com/auth/youtube.readonly"
    youtube_upload = "https://www.googleapis.com/auth/youtube.upload"
    youtube = "https://www.googleapis.com/auth/youtube"
    youtubepartner = "https://www.googleapis.com/auth/youtubepartner"


class GoogleCalendarScopes(Enum):
    calendar = "https://www.googleapis.com/auth/calendar"
    calendar_events = "https://www.googleapis.com/auth/calendar.events"
    calendar_settings_readonly = (
        "https://www.googleapis.com/auth/calendar.settings.readonly"
    )


class GoogleDriveScopes(Enum):
    metadata = "https://www.googleapis.com/auth/drive.metadata"
    files = "https://www.googleapis.com/auth/drive.file"
    drive = "https://www.googleapis.com/auth/drive"
    activity = "https://www.googleapis.com/auth/drive.activity"
