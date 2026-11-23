"""Entry point for ``manimgx inspect``: the video named by ``EXPLAIN_VIDEO`` as a scene class.

``manimgx inspect`` builds scenes without arguments, so this wraps ``VideoScene`` for the
video directory in the environment. ``plan_check.py`` runs it as a second opinion on layout.
"""

import os

from explain.paths import Video
from explain.scene import VideoScene, configure
from explain.styles import load_style


class InspectedVideo(VideoScene):
    """The video in ``EXPLAIN_VIDEO``, constructible without arguments."""

    def __init__(self) -> None:
        """Open the video named by ``EXPLAIN_VIDEO`` and configure manimgx for its style.

        Raises:
            KeyError: If ``EXPLAIN_VIDEO`` is not set.
        """
        video = Video.at(os.environ["EXPLAIN_VIDEO"])
        style = load_style(video.style_name)
        configure(style)
        super().__init__(video, style)
