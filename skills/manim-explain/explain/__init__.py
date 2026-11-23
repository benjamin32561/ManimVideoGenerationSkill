"""manim-explain pipeline package.

Shared by the command-line steps in ``scripts/`` and by the manimgx scene runtime:

* ``paths``    where a video's files live (``demos/<series>/<slug>/``) and where it is delivered
* ``styles``   style packs (``styles/<name>/style.yaml``): voice, speaker profile, narrative
               parameters, visual tokens, text policy, motion numbers
* ``script``   the narrated script (``script.yaml``) and its narrative grammar
* ``timing``   Whisper words, beat boundaries, and anchor phrases resolved to seconds
* ``plan``     the layout plan (``plan/layout.json``) and the timed events (``plan/events.json``)
* ``objects``  layout objects built as manimgx mobjects
* ``actions``  the action vocabulary that turns events into animations
* ``scene``    the scene that plays a video's events against its narration
* ``probe``    geometry sampled while a scene runs (no pixels drawn), cached per window
* ``windows``  window and beat digests: what each stretch of the film depends on
* ``device``   where manimgx draws: the CPU by default, named GPUs only
* ``worker``   one beat's render process
* ``review``   sync measurement and review frames of a rendered video
* ``media``    ffmpeg helpers: frame encoding, stitching, muxing, probing
* ``openrouter`` TTS and STT requests
"""
