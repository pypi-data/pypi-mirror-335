from plexflow.core.context.partial_context import PartialContext
from datetime import datetime as dt
from plexflow.core.subtitles.providers.oss.oss_subtitle import OSSSubtitle
from typing import List

class Subtitles(PartialContext):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def all(self) -> List[OSSSubtitle]:
        return self.get("subtitles/oss")

    def update(self, subtitles: List[OSSSubtitle]):
        if len(subtitles) == 0:
            return
        self.set("subtitles/oss", subtitles)
