# TTS: finding a better narration voice

Started 2026-11-21. Goal: replace or beat the current narration voice (xAI Grok Voice
`x-ai/grok-voice-tts-1.0`, voice `leo`, speed 0.95, via OpenRouter), which Ben rates "kinda mid",
for long-form, calm, intelligent explainer narration in the 3Blue1Brown / Welch Labs register.

Reference pace (from [synthesis.md §3](synthesis.md#3-language) and
[styles/landscape.md](styles/landscape.md)): 3Blue1Brown 175–200 wpm, Welch Labs about 170,
Core Dumped (ElevenLabs brand voice) 182–201 articulation wpm. Our 47 demos: median 139 wpm.

Claims are marked **[verified: source]**, **[measured]** (by us, on the samples in
`research_cache/tts-samples/`) or **[inferred: from what]**.

Status: done 2026-11-21 (research, 37 sample pairs, measurements). Ben's listening verdict is
still open.

## 1. Verdict

**ElevenLabs Eleven v4 is the strongest candidate on the evidence: it shares #1 on the
Artificial Analysis arena (Elo 1340 vs Grok's 1160 at #31), and its direct API returns
character timestamps, which would let us drop the Whisper pass.** Two cheaper runners-up:
**Speechify Simba 3.5** (arena #6; returns word timestamps in the same JSON as the audio;
among the fastest of our samples at 164 / 187 wpm) and **Gemini 3.8 Flash TTS** (arena #7; cheapest; pace
can be steered by the prompt; no timestamps, but it stays inside OpenRouter, so the
"OpenRouter only" rule survives). The best local option is **Kyutai TTS 1.6B**. It runs on a
V100 in fp32, and its native word timings agree with Whisper to about 0.06 s once a fixed
offset is removed [measured]. These rankings come from arena votes and measurements. I could
not listen to the samples; Ben's ears decide (§3).

Things we found along the way:
- OpenRouter now serves 40 TTS models, ElevenLabs among them, so every top hosted voice except
  Cartesia, Inworld and MiniMax can be heard with the key we already have. OpenRouter returns
  audio only, never timestamps [verified: OpenRouter TTS guide].
- Our `speed: 0.95` for Grok does nothing through OpenRouter: speeds of 0.75, 0.95 and 1.0 gave the
  same length [measured]. Eleven v4 rejects `speed` outright (400), and v3 at 1.15 barely
  changed pace [measured].
- Almost every model read our texts at 130–192 wpm (median 151 on t1, 161 on t2). Only 9 of
  37 voices reached the 3Blue1Brown band of 175–200 on the flowing text t2, and only 2 did on t1.
  The choppy t1 ran slower than t2 for 32 of 37 voices (median 11 wpm slower, up to 32), so
  script style moves pace about as much as voice choice does [measured].

## 2. Comparison table

wpm is measured on our samples (t1 / t2); Elo and rank are from the AA arena; $/min assumes
1,050 characters per minute. "Direct" means the provider's own API, which needs its own key.

| Option | How we'd call it | AA Elo (rank) | wpm t1 / t2 | Pace · pauses · emphasis · pronunciation | Native timestamps | Voices · cloning | $/min | Licence |
|---|---|---|---|---|---|---|---:|---|
| **Grok Voice** (baseline) | OpenRouter / direct `XAI_API_KEY` | 1160 (#31) | 160 / 166 | speed ignored via OpenRouter [measured]; direct: speed 0.7–1.5, `[pause]`, `<slow>`, `<emphasis>`, `replace` map | char, direct only | 5 via OpenRouter, 26 direct; clone ≤ 120 s | 0.016 | hosted |
| **ElevenLabs v4** | OpenRouter / direct `ELEVENLABS_API_KEY` | **1340 (#1)** | 142–149 / 155–163 | no speed (400) [measured], no break tag; audio tags, inline IPA, pronunciation dictionaries | **char** (`/with-timestamps`), direct only | 21 default + 10k library; instant / pro cloning | 0.084 | hosted |
| ElevenLabs v4 Turbo | same | 1340 (#1) | 144 / 155 | same | char, direct | same | 0.042 | hosted |
| ElevenLabs Multilingual v2 | same | 1092 (#53) | 156–158 / 172–176 | speed 0.7–1.2, dictionaries | char, direct | same | 0.084 | hosted |
| **Speechify Simba 3.5** | OpenRouter / direct (plan key) | 1293 (#6) | **164 / 187** | speed 0.5–2, SSML `<break>`, `<prosody>`, `<sub>`, pronunciations | **word** (`speech_marks`), direct only | 900+; cloning on paid plans | 0.012–0.016 | hosted |
| **Gemini 3.8 Flash TTS** | OpenRouter / `GEMINI_API_KEY` | 1282 (#7) | 142 / 147; **160 / 178** with a brisk-pace prompt | no speed param, no SSML; style prompt, `<short pause>`, caps for emphasis | none | 30 voices; voice design / replication (region-limited) | 0.014 → 0.028 (2027) | hosted |
| Cartesia Sonic 3.6 | direct `CARTESIA_API_KEY` (not on OpenRouter) | 1294 (#5) | not sampled | speed 0.6–1.5, `<break>`, `<emotion>`, IPA, dictionaries | **word + phoneme** | narrator voices; instant clone ($5 plan) | 0.04–0.07 | hosted |
| Inworld TTS-2 | direct `INWORLD_API_KEY` (not on OpenRouter) | 1269 (#10) | not sampled | rate 0.5–1.5, `<break/>`, `[say calmly]`, IPA | **word / char + phonemes** | free instant cloning | 0.026 | hosted |
| Fish S2.1 Pro / Drama 3 | OpenRouter / direct `FISH_API_KEY` | 1181 (#25) / 1277 (#8) | Ethan 166 / 184; Drama 131 / 151 | speed 0.5–2, free-form `[bracket]` direction | segments (granularity unstated), direct only | any library voice; clone 10–30 s | 0.016 / 0.010–0.05 | hosted |
| MAI-Voice-2.1 | OpenRouter / Azure `SPEECH_KEY` | not listed | Grant 153 / 168 | speed 0.5–2; `narrator` / `educational` styles need direct SSML | unverified | 12 English voices; gated cloning | 0.023 | hosted |
| Voxtral TTS 3 | OpenRouter / `MISTRAL_API_KEY` | 1211 (#21) | 160–166 / 184–192 | emotion-suffixed presets, no speed | none | presets; cloning | 0.014 | hosted |
| MiniMax Speech 2.8 HD | direct (not on OpenRouter) | 1173 (#28) | not sampled | speed 0.5–2, `<#0.5#>` pauses, IPA dictionary | **word** | narrator presets; clone $1.5 | 0.105 | hosted |
| **Kyutai TTS 1.6B** | local, V100 fp32, 7.6 GiB | unranked | 145–165 / 149–160 | voice embeddings only, `padding_between`, no speed knob | **word** (measured) | hundreds of preset embeddings (voice donations, Expresso, VCTK, EARS); no raw-audio cloning | GPU only | CC-BY-4.0 |
| Kokoro-82M | local, 1 GiB | 1060 (#68) | 150–158 / 161–172 | `speed`, G2P | **token** (measured) | 54 presets; no cloning | GPU only | Apache-2.0 |
| Ming-3.0-tts-0.5B | local, 2.9 GiB (bf16 emulated) | 1179 (open #3) | 151–176 / 163–179 | speed, emotion, freeform prompt | none | UK_George, US_Emma; cloning | GPU only | MIT |
| VoxCPM2 | local, fp32, 10.4 GiB | unranked | 155–162 / 174–187 | voice design from a description | none | design / cloning | GPU only | Apache-2.0 |
| Qwen3-TTS 1.7B | local fp16 / OpenRouter | "Qwen3 TTS" 928 (#95), variant unclear | 150–159 / 148–152 local | plain-language instruct, presets | none | presets, design, 3 s clone | GPU only / 0.021 | Apache-2.0 |

## 3. Listen first

These are ranked by arena standing, measured pace and whether the option would drop Whisper.
I did not listen to them. Files are in `research_cache/tts-samples/`; each name below takes
`_t1.mp3` / `_t2.mp3` (t2 is the better test of flowing explainer delivery).

1. `00_xai_grok-voice-tts-10_leo` — the baseline, to calibrate "mid".
2. `01_elevenlabs_eleven-v4_george` and `02_elevenlabs_eleven-v4_brian` — the arena leader,
   and the pick if they win by ear. George is British ("warm, captivating storyteller"), Brian
   American ("deep, resonant, comforting") [verified: ElevenLabs public voice list]. Note the
   slower pace (142–163 wpm), which v4 has no speed knob to fix.
3. `19_speechify_simba-35_henry` — arena #6, one of the few to reach 3b1b pace without
   prompting (164 / 187), word timestamps on the direct API, and the cheapest of the top group. The voice
   was picked blind from a list of 20 names; other Simba voices may suit better.
4. `27_google_gemini-38-flash-tts_charon` (brisk-pace prompt) next to `08_…_charon` (default
   narrator prompt) — shows that Gemini's pace follows the prompt (+12–20 % wpm), and it is the
   no-policy-change option.
5. `62_local_kyutai-tts16b_ex03calm` / `63_local_kyutai-tts16b_ex04narration` — the best local
   option with native word timings, if Ben would rather run things himself.
6. `05_elevenlabs_eleven-multilingual-v2_george` — the older ElevenLabs narration model
   (likely what most ElevenLabs-voiced explainers used before v3 [inferred]); faster
   (156–172), and ElevenLabs pitches it as the most stable for long-form.
7. `14_fishaudio_s21-pro_ethan` and `16_fishaudio_drama-3_ethan` — cheap, quick, any Fish
   library voice; Drama 3 is arena #8.
8. `67_local_ming30tts05b_freeform-narrator` — the best-ranked open model that runs here (MIT),
   with brisk pace (176–179).

To hear the strong providers we could not sample: Cartesia's narrator page lets you type up to
500 characters without signing up, <https://cartesia.ai/voices/narrator-voice> (Romeo, Carl)
[verified: research agent fetch]. MiniMax's demo is at <https://www.minimax.io/audio> (sign-up
not checked). Inworld's playground (platform.inworld.ai/tts-playground) probably needs a login.
ElevenLabs' own v4 samples are at <https://elevenlabs.io/v4>, though ours (01/02) are the same
model.

Probably skip: `23_qwen_qwen3-tts-17b_ryan` (113 wpm with no pauses on t2, a drawl),
`20_deepgram_flux-tts_flux-marcus-en` (Whisper heard "hold" for "hole" and lost a "leaves"),
`25_qwen_qwen-audio-30-tts-plus_longanlufeng` ("corroded", "ion" for "anion") [measured:
Whisper transcripts].

## 4. OpenRouter TTS catalogue (what we can call today with our one key)

OpenRouter now serves **40 speech models** through `POST /api/v1/audio/speech`, up from the
handful `tts-stt.md` knows about **[verified: `GET /api/v1/models?output_modalities=speech`,
2026-11-21; saved to `research_cache/tts-samples/work/speech_models.json`]**. That includes
ElevenLabs (v4, v4 Turbo, v3, Multilingual v2, Flash/Turbo), Gemini 3.8 Flash / Flash-Lite /
2.5 Pro TTS, Microsoft MAI-Voice-2 / 2.1, Fish Audio S1 / S2 Pro / S2.1 Pro / Drama 3,
Speechify Simba 3.5, Mistral Voxtral TTS 3, Deepgram Aura-2 / Flux, HeyGen Voice, AssemblyAI
TTS-1, Qwen-Audio-3.0 TTS, Qwen3-TTS 1.7B, ByteDance Seed Audio 1.0, plus the open Kokoro,
Orpheus and CSM.

What OpenRouter gives and doesn't give **[verified: [OpenRouter TTS guide](https://openrouter.ai/docs/guides/overview/multimodal/tts)]**:

- The response is a **raw audio byte stream only**, with an `X-Generation-Id` header. There is
  **no timestamp or alignment option** on the OpenRouter endpoint, even for providers whose own
  API returns them (ElevenLabs, xAI, Fish, Speechify). So any model reached through OpenRouter
  still needs our Whisper pass.
- Request fields: `model`, `input` (string or multi-speaker turns), `voice`, `instructions`
  (honoured by Gemini TTS, Fish and OpenAI models only), `response_format` (`mp3` or `pcm`;
  Gemini and HeyGen are `pcm` only), `speed`, `input_references` (stateless voice cloning from
  1–3 reference clips on Fish, HeyGen, Seed, Voxtral), `provider` (routing plus
  `provider.options.<slug>` passthrough).
- `speed` ranges published per model by `GET /api/v1/audio/speech/models`: ElevenLabs v3 /
  Multilingual v2 / Flash 0.7–1.2, Fish and MAI-Voice and Speechify 0.5–2, Kokoro / Orpheus /
  CSM 0.25–4. **Grok Voice publishes no speed range, and through OpenRouter it ignores
  `speed`**: t1 came out 20.86 / 20.21 / 20.21 s at speed 0.75 / 0.95 / 1.0 [measured].
  ElevenLabs v4 publishes no range either and rejects the field with a 400 ("speed is not
  supported by eleven_v4") [measured].
- Voice lists are short: OpenRouter exposes only **5 of xAI's 26** built-in voices (eve, ara,
  rex, sal, leo) and 21 ElevenLabs default voices (not the 10,000-voice library). Fish models
  publish no list; any public Fish Voice Library `reference_id` works as `voice` [measured: we
  used Fish's official "Ethan" `536d3a5e…` and "Adrian" `bf322df2…`].
- Pricing is per input character (Seed Audio per second; Gemini per token). Prices are the
  same as the providers' own pay-as-you-go rates where we could compare (ElevenLabs v4
  $80 / 1M chars, Grok $15 / 1M, Fish S2.1 Pro $15 / 1M).
- `openai/gpt-4o-mini-tts` is **not** served (400 "does not exist") [measured]. OpenAI's TTS
  models are deprecated anyway (below).

## 5. Hosted providers: per-option notes

Cost per minute assumes **about 1,050 characters per minute of narration** (our two texts
average 5.7 characters per word including spaces; at 175–185 wpm that is 1,000–1,100 chars)
[inferred: from the two bench texts]. Arena numbers: **AA** = Artificial Analysis Speech
Arena, read 2026-11-21, no update date on the page, short general prompts rather than long
technical narration [verified: [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard)].
**TTS Arena V2** = Hugging Face TTS-AGI arena, read through its Space API [verified:
[TTS Arena V2](https://huggingface.co/spaces/TTS-AGI/TTS-Arena-V2)].

AA top 10 (Elo): Eleven v4 Turbo 1340, Eleven v4 1340, StepAudio 3 TTS 1307,
Qwen-Audio-3.1-TTS-Plus 1298, Cartesia Sonic 3.6 1294, Speechify Simba 3.5 1293, Gemini 3.8
Flash TTS 1282, Fish Audio Drama 3 1277, Smallest.ai Lightning V3.1 Pro 1276, Inworld Realtime
TTS-2 1269. Further down: AssemblyAI-TTS-1 #20 (1212), Voxtral 3 TTS #21 (1211), Eleven v3 #24
(1191), Fish S2.1 Pro #25 (1181), MiniMax Speech 2.8 HD #28 (1173), **"SpaceXAI TTS" (Grok)
#31 (1160)**, Eleven Multilingual v2 #53 (1092), Kokoro #68 (1060), Gemini 2.5 Pro TTS #79
(1038), MAI-Voice-1 #85 (1024). HeyGen and MAI-Voice-2.x are not listed.
TTS Arena V2 top: an unnamed "Aurora", MiniMax Speech 02 HD, Gradium, Inworld TTS 1.5 MAX,
Hume Octave, Eleven v3; Eleven v4, Google, Azure and OpenAI are not on it.

### ElevenLabs — Eleven v4 (Sept 2026), v3, Multilingual v2

- **Quality:** Eleven v4 and v4 Turbo share AA #1 (1340). v3 #24, Multilingual v2 #53.
  Multilingual v2 is the model ElevenLabs still calls the most stable for long-form
  [verified: [ElevenLabs models](https://elevenlabs.io/docs/models)].
- **Control:** no SSML `<break>` on v3/v4 (use punctuation, dashes, ellipses); inline audio
  tags such as `[whispers]`, `[sighs]` and plain-language direction on v3/v4; inline IPA
  between slashes on v4 (`phoneme` tags only on Flash v2); pronunciation dictionaries (alias
  and phoneme rules, up to 3 per request); `speed` 0.7–1.2 on v3 / Multilingual v2 / Flash
  (v4 rejects it through OpenRouter, and v3 at 1.15 barely moved pace [measured]);
  `previous_text` / `next_text`
  for continuity across chunks [verified: [controls](https://elevenlabs.io/docs/best-practices/prompting/controls),
  [with-timestamps](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)].
- **Timestamps: native, character level.** `POST /v1/text-to-speech/{voice_id}/with-timestamps`
  (and a streaming variant) returns `audio_base64` plus `alignment` and
  `normalized_alignment`, each with `characters`, `character_start_times_seconds`,
  `character_end_times_seconds`. Words are built by splitting on spaces. Any model with
  `can_do_text_to_speech` is accepted; v4 support is not stated explicitly [verified: same page].
- **Voices / cloning:** 21 default voices (George = warm British storyteller, Brian = deep
  American, Daniel = broadcaster, Alice = educator), a 10,000+ community library, instant
  cloning from about 10 s of audio (Starter, $6/mo) and professional cloning (Creator,
  $22/mo) [verified: public `GET https://api.elevenlabs.io/v1/voices` labels, [pricing](https://elevenlabs.io/pricing)].
- **Cost:** API pay-as-you-go $0.08 / 1k chars for v4 and Multilingual v2 (about
  **$0.084/min**), $0.04 for v4 Turbo / Flash (about $0.042/min) [verified: [API pricing](https://elevenlabs.io/pricing/api)].
  Through OpenRouter: same rates, measured $0.08 / 1k chars [measured].
- **Access:** `ELEVENLABS_API_KEY` (`xi-api-key` header); v4 takes up to 100,000 chars per
  request. Listen: <https://elevenlabs.io/v4> and the voice library pages (sign-up-free
  playback not checked).

### Google — Gemini 3.8 Flash TTS (Sept 2026), Chirp 3 HD

- **Quality:** Gemini 3.8 Flash TTS AA #7 (1282), Flash-Lite #12 (1261), 3.1 Flash #18;
  Chirp 3 HD #67 (1060) [verified: AA].
- **Control:** natural-language style prompt (OpenRouter sends `instructions` as
  `speech_metadata.style`), inline tags such as `<short pause>`, `<long pause>`, `<sigh>`,
  capitals for emphasis; **no speed parameter and no SSML** — pace is asked for in the prompt
  [verified: [Gemini speech generation](https://aistudio.google.com/docs/speech-generation)].
  Chirp 3 HD instead has `speaking_rate` 0.25–2, `[pause]` markup, IPA custom pronunciations
  and preview SSML [verified: [Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)].
- **Timestamps: none** for Gemini TTS. Cloud TTS returns timepoints only for SSML `<mark>`,
  which Chirp 3 HD does not support (Neural2 / Studio / WaveNet do) [verified:
  [v1beta1 synthesize](https://docs.cloud.google.com/text-to-speech/docs/reference/rest/v1beta1/text/synthesize);
  Chirp 3 HD conclusion inferred from its missing `<mark>`].
- **Voices / cloning:** 30 prebuilt voices (Charon "informative", Sadaltager
  "knowledgeable", Iapetus "clear", Schedar "even", Gacrux "mature"); voice design and voice
  replication from 30 s plus a consent recording, not available in the EEA, UK, Switzerland,
  India, Illinois, Texas [verified: [Gemini 3.8 TTS blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/)].
- **Cost:** $9 / 1M audio tokens at 25 tokens/s, about **$0.0135/min** until 2026-12-31,
  then $18 / 1M (about $0.027/min) [verified: [Gemini pricing](https://aistudio.google.com/docs/pricing)].
  Measured through OpenRouter: $0.0136 per minute of audio [measured: billed cost / duration].
- **Access:** `GEMINI_API_KEY`; up to about 11 minutes of audio per call. Samples are embedded in
  the blog post above; AI Studio's playground needs a Google login.

### Microsoft — MAI-Voice-2.1, Azure Neural / Dragon HD

- **Quality:** MAI-Voice-2.x is not on AA yet (MAI-Voice-1 #85, Azure HD 2.5 #36, Azure
  Neural #82) [verified: AA].
- **Control:** full Azure SSML on Neural voices (`prosody`, `break`, `emphasis`, `phoneme`,
  lexicons, `bookmark`); MAI-Voice-2.1 supports `mstts:express-as` styles including
  `narrator`, `educational` and `audiobook` and is pitched at long-form [verified:
  [MAI voices](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-voices)].
  OpenRouter hides SSML, so these styles are unreachable from our key.
- **Timestamps:** Azure Neural and Dragon HD Omni emit **WordBoundary** events (audio offset
  and duration per word) [verified: [speech synthesis how-to](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-speech-synthesis),
  [HD voices](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices)];
  whether MAI-Voice voices emit them is unverified.
- **Cost:** Neural $15 / 1M chars (about $0.016/min), HD $22 / 1M; MAI-Voice-2.1 $22 / 1M on
  OpenRouter (about $0.023/min) [verified: Azure retail prices API; OpenRouter].
- **Access:** `SPEECH_KEY` + `SPEECH_REGION`. Playground needs an Azure login.

### Speechify — Simba 3.5 (Nov 2026)

- **Quality:** AA #6 (1293), the cheapest model in the AA top 10 [verified: AA].
- **Control:** SSML `<break>`, `<prosody rate/pitch/volume>`, `<sub>`; a `pronunciations`
  parameter; speed 0.5–2 on OpenRouter [verified: [Speechify TTS API](https://speechify.ai/text-to-speech-api)].
- **Timestamps: native, word level.** Non-streaming `POST /v1/audio/speech` returns base64
  audio plus `speech_marks` (`start_time` / `end_time` in ms, character offsets) in one JSON;
  `POST /v1/audio/stream/with-timestamps` streams them; Simba 3.0/3.2/3.5 mark word by word
  [verified: [Speechify with-timestamps](https://docs.speechify.ai/build/api-reference/v1/audio/stream/with-timestamps)].
- **Voices / cloning:** 900+ voices; cloning on paid plans.
- **Cost:** subscription only: $15 / 1M on Starter ($10/mo), $12 on Pro, $10 on Scale
  (about $0.011–0.016/min); OpenRouter charges $11.25 / 1M [verified: [Speechify pricing](https://speechify.ai/pricing); OpenRouter].
- **Access:** Bearer key from platform.speechify.ai; 20,000 billable chars per request.

### Cartesia — Sonic 3.6 (Aug 2026) — not on OpenRouter

- **Quality:** AA #5 (1294) [verified: AA].
- **Control:** SSML-like tags `<break time="1s"/>`, `<speed ratio>` (0.6–1.5), `<volume>`,
  `<emotion>` (beta), `<spell>`; `generation_config.speed` 0.6–1.5; inline IPA and
  pronunciation dictionaries [verified: [Sonic 3 SSML tags](https://docs.cartesia.ai/build-with-cartesia/sonic-3/ssml-tags),
  [custom pronunciations](https://docs.cartesia.ai/build-with-cartesia/capability-guides/custom-pronunciations)].
- **Timestamps: native, word and phoneme level** (`add_timestamps`, `add_phoneme_timestamps`)
  on WebSocket and `POST /tts/sse` [verified: [SSE API](https://docs.cartesia.ai/api-reference/tts/sse)].
- **Voices / cloning:** narrator voices Romeo, Marian, Carl, Edna; instant cloning from the
  $5 Pro plan, professional from $49 Startup [verified: [pricing](https://cartesia.ai/pricing)].
- **Cost:** subscription credits, overage $38–65 / 1M chars (about $0.04–0.07/min).
- **Access:** `CARTESIA_API_KEY` (Bearer + `Cartesia-Version` header). **Listen without
  signing up:** <https://cartesia.ai/voices/narrator-voice> (500-character box) [verified:
  agent fetch of that page].

### Inworld — Realtime TTS-2 — not on OpenRouter

- **Quality:** AA #10 (1269); TTS 1.5 MAX is #5 on TTS Arena V2 [verified: AA, TTS Arena V2].
- **Control:** `speakingRate` 0.5–1.5, bracket steering such as `[say calmly]`, `<break/>`,
  inline IPA, voice design from a prompt [verified: [synthesize API](https://docs.inworld.ai/api-reference/ttsAPI/texttospeech/synthesize-speech)].
- **Timestamps: native, word or character level** (`timestampType: "WORD"` returns
  `wordAlignment {words, wordStartTimeSeconds, wordEndTimeSeconds, phoneticDetails}`), sync
  and streaming, on `inworld-tts-2` and `-flash` [verified: [Inworld timestamps](https://docs.inworld.ai/tts/capabilities/timestamps)].
- **Voices / cloning:** "Victor" narrator; free instant cloning from 3–30 s.
- **Cost:** $25 / 1M PAYG (about $0.026/min), $12.50 on Growth [verified: [Inworld pricing](https://inworld.ai/pricing)].
- **Access:** `INWORLD_API_KEY` (Basic auth); 2,000 chars per sync request (4,000 streaming)
  — our chunking already fits. Playground: platform.inworld.ai/tts-playground (login unverified).

### Fish Audio — Drama 3, S2.1 Pro

- **Quality:** Drama 3 AA #8 (1277), S2.1 Pro #25 (1181) [verified: AA].
- **Control:** `prosody.speed` 0.5–2; free-form `[bracket]` direction on S2.x; Drama 3 is
  "directed" in plain language; OpenRouter turns `instructions` into a leading bracket tag
  [verified: [Fish TTS guide](https://docs.fish.audio/developer-guide/core-features/text-to-speech); OpenRouter guide].
- **Timestamps: native, granularity not stated.** `POST /v1/tts/stream/with-timestamp` (SSE)
  returns `alignment.segments[] {text, start, end}` per chunk plus `chunk_audio_offset_sec`;
  examples look word-level [verified: [Fish with-timestamp](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech-stream-with-timestamps)].
- **Voices / cloning:** any public Voice Library `reference_id`; instant cloning from 10–30 s
  plus transcript, no plan needed.
- **Cost:** S2.1 Pro $15 / 1M UTF-8 bytes (about $0.016/min); Drama 3 $50 / 1M list
  ($10 promo to 2026-11-30); S1 retires 2026-12-31 [verified: [Fish pricing](https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits)].
- **Access:** `FISH_API_KEY`. Voice pages on fish.audio play samples.

### xAI — Grok Voice TTS (current baseline)

- **Quality:** AA #31 (1160, listed as "SpaceXAI TTS") [verified: AA].
- **Control (direct API):** `speed` (0.7–1.5 on the WebSocket), speech tags `[pause]`,
  `[long-pause]`, `[breath]`, wrapping tags `<slow>`, `<emphasis>`, `<soft>`,
  `<lower-pitch>`; a `replace` pronunciation map (200 entries, respellings or IPA)
  [verified: [xAI voice API](https://docs.x.ai/developers/rest-api-reference/inference/voice)].
- **Timestamps: native, character level, direct API only.** `with_timestamps: true` returns
  `audio_timestamps {graph_chars[], graph_times[{start, end}]}` [verified: same page].
- **Voices / cloning:** **26 built-in voices on the direct API** (Orion, Atlas, Helios, Kepler,
  Sirius, … plus the 5 OpenRouter exposes); custom voices from a clip of up to 120 s.
- **Cost:** $15 / 1M (about $0.016/min); measured $0.015 / 1k chars on OpenRouter [measured].
- **Access:** `XAI_API_KEY`; 60,000 chars per request.

### MiniMax — Speech 2.8 HD — not on OpenRouter

- **Quality:** AA #28 (1173); older Speech 02 HD is #3 on TTS Arena V2 [verified: AA, TTS Arena V2].
- **Control:** pause markers `<#0.5#>`, `speed` 0.5–2, `emotion` (includes "calm"),
  IPA pronunciation dictionary [verified: [MiniMax T2A HTTP](https://platform.minimax.io/docs/api-reference/speech-t2a-http)].
- **Timestamps: native, word level** (`subtitle_enable: true`, `subtitle_type: "word"`).
- **Voices:** `English_expressive_narrator`, `English_Trustworth_Man`, `English_CalmWoman`.
- **Cost:** HD $100 / 1M (about $0.105/min), Turbo $60 / 1M [verified: [MiniMax pricing](https://platform.minimax.io/docs/guides/pricing-paygo)].
- **Access:** Bearer key (env name unverified); demo at minimax.io/audio (sign-up unverified).

### Others, briefly

- **Mistral Voxtral TTS 3:** AA #21 (1211), $13 / 1M, emotion-suffixed preset voices
  (`en_paul_neutral`, `gb_oliver_neutral`), `expressiveness` 1–5, no speed, **no timestamps**
  [verified: [Mistral TTS docs](https://docs.mistral.ai/studio/audio/text-to-speech/generate-speech)].
  On OpenRouter.
- **AssemblyAI TTS-1:** AA #20 (1212), $15 / 1M, on OpenRouter; timestamps not researched.
- **Deepgram Aura-2 / Flux TTS:** agent-oriented; Flux AA #71 (1052); no TTS timestamps
  documented [verified: [Flux TTS](https://developers.deepgram.com/docs/flux-tts/feature-overview)].
- **HeyGen Voice:** on OpenRouter only as `pcm`, no speed, audio tags; not on AA.
- **ByteDance Seed Audio 1.0** (OpenRouter): treats `input` as a prompt rather than text to read
  verbatim, $0.0025 per second of audio (about $0.15/min), 120 s cap [verified: OpenRouter TTS
  guide]. Not sampled, since narration has to be read word for word.
- **Qwen-Audio-3.1-TTS-Plus:** AA #4 (1298) but only the older 3.0 Plus (#11) is on
  OpenRouter, with two Chinese-named voices.
- **StepAudio 3 TTS** (AA #3, launched 2026-09-15, `stepaudio-3-tts` on StepFun's
  `/v1/audio/speech`): price reported as $14 / 1M (AA) or $36 / 1M (press), no TTS timestamps
  found [unverified: search results only, StepFun docs not read]. Not on OpenRouter.
- **Smallest.ai Lightning V3.1 Pro** (AA #9): about $19.50 / 1M chars; per-word timestamps on
  the WebSocket endpoint (`word_timestamps: true`), none on REST [unverified: search results
  citing [Smallest changelog](https://docs.smallest.ai/models/changelog/lightning-v-3-1)]. Not on OpenRouter.
- **Rime Coda v2** (AA #42, word timestamps on its WebSocket), **Murf Falcon 2.1** (AA #34,
  word timestamps on its WebSocket, $10 / 1M), **WellSaid** (word-timing endpoint, quote-based
  pricing): below the quality bar or enterprise-only [verified: [Rime](https://docs.rime.ai/docs/websockets),
  [Murf](https://murf.ai/api/docs/text-to-speech/web-sockets/advanced-settings), [WellSaid](https://docs.wellsaidlabs.com/reference/using-word-timing-with-the-wellsaid-api)].
- **OpenAI:** `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts` were deprecated on 2026-10-01 and shut down on
  2027-01-06; the named replacement is Realtime-API only; no timestamps ever [verified:
  [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)]. Skip.
- **Amazon Polly:** Generative AA #66, Long-Form #83; speech marks (word timing) on Neural and
  Long-form but not Generative [verified: [Polly speech marks](https://docs.aws.amazon.com/polly/latest/dg/speechmarks.html)].
  Below the bar.
- **Gone:** Hume (developer docs now list only Audio Decisions and Expression Measurement
  [verified: [dev.hume.ai/llms.txt](https://dev.hume.ai/llms.txt)]; TTS end date 2026-11-13 from a
  secondary source only), LMNT ("our speech generation journey has come to an end"
  [verified: [LMNT docs](https://docs.lmnt.com/build-with-lmnt/word-timestamps)]), Resemble AI (no longer sells
  generative voices [verified: [Resemble docs](https://docs.resemble.ai/)]).

## 6. Open models: per-option notes and local runs

Research summary (local run results are added below as they land). Open-weights arena (AA,
read 2026-11-21): Fish Audio Drama 3 1277, Breeze TTS 2 1228, Ming-3.0-tts 1179, Phonon 31M
1108, Fish S2 Pro 1101, Step-Audio-EditX 1100, Voxtral 1094, Magpie 357M 1064, Kokoro 1060,
Maya1 1047, OpenAudio S1-mini 1042, Higgs V3 1035, Chatterbox 1019, Zonos 1000, VibeVoice-1.5B
954 [verified: [AA open weights](https://artificialanalysis.ai/text-to-speech/leaderboard/open-weights)].
Qwen3-TTS, CosyVoice 3, Kyutai TTS, MOSS-TTS and Dia2 are unranked there.

**V100 constraints** [verified: [PyTorch dev-discuss](https://dev-discuss.pytorch.org/t/dropping-volta-support-from-cuda-12-8-binaries-for-release-2-11/3290)]:
PyTorch CUDA 12.8/12.9 wheels dropped Volta from 2.11; cu126 wheels still include `sm_70`
(we run `torch 2.8.0+cu126`, arch list includes `sm_70` [measured]). A proposal makes 2.14
the last cu126 release. vLLM 0.20+ reportedly lacks V100 support, so models that ship only
through vLLM / SGLang (Voxtral open weights, Higgs Audio V3, ZONOS2) are poor fits.

**Native timestamps among open models:** only **Kokoro** (per token `start_ts`/`end_ts`),
**Kyutai TTS 1.6B** (per word, from its delayed-streams text channel) and **Dia2** (per word)
[verified: [kokoro pipeline.py](https://raw.githubusercontent.com/hexgrad/kokoro/main/kokoro/pipeline.py),
[moshi tts.py](https://raw.githubusercontent.com/kyutai-labs/moshi/main/moshi/moshi/models/tts.py),
[Dia2 card](https://huggingface.co/nari-labs/Dia2-2B)].

| Model | Licence (weights) | Size | Timestamps | Control | V100 notes |
|---|---|---|---|---|---|
| Kokoro-82M v1.0 | Apache-2.0 | 82M | per token | `speed`, misaki G2P | ran, 1 GiB [measured] |
| Kyutai TTS 1.6B en/fr | CC-BY-4.0 (code MIT) | 1.8B | per word | voice embeddings, no cloning from raw audio | loader defaults to bf16; ran in fp32 [measured] |
| Qwen3-TTS-12Hz-1.7B | Apache-2.0 | 1.7B | none | plain-language `instruct`, presets Aiden/Ryan, 3 s cloning (Base) | FA2 optional; ran fp16 + SDPA [measured] |
| Ming-3.0-tts-0.5B | MIT | 0.5B | none | speed, pitch, emotion; UK_George, US_Emma | upstream tests only H800/H20; ran here in shipped bf16 [measured] |
| VoxCPM2 | Apache-2.0 | 2B | none | voice design from a description, 48 kHz | bf16 weights; ran in forced fp32 [measured] |
| CosyVoice 3 (0.5B) | Apache-2.0 | 0.5B | none | speed, instruct, `[breath]`, CMU phonemes, cloning | `fp16=` flag |
| MOSS-TTS v1.5 | Apache-2.0 | 8B / 4B | none | target duration, `[pause 3.2s]`, IPA, cloning | SDPA below sm80 |
| IndexTTS-2.5 | bilibili licence (commercial < 100M MAU) | 0.8B | none | `duration_factor`, emotion vector, cloning | `use_bf16=False` |
| Fish S2 Pro | Fish research licence (non-commercial) | 5B | none | `[pause]`, cloning | `--half`, ≥ 24 GB |
| Fish Drama 3 | unclear (community / research) | 35B MoE, FP8 experts | none | directed tags | **won't fit one V100** (≥ 48 GB) |
| Dia2-2B | Apache-2.0 | 2B | per word | dialogue-first, unstable voice without prefix clip, 2 min cap | fp32 only on V100 |
| Chatterbox | MIT | 0.5B | none | no speed | **retired Aug 2026**, watermarked |
| VibeVoice 1.5B / Realtime-0.5B | MIT, research-only | | none | | 7B and TTS code pulled 2025-09 |

Sources for the table: model cards and repos listed in §9 (Open models). Licences were
re-checked through the Hugging Face API tags (Kyutai `cc-by-4.0`, Kokoro / Qwen3-TTS / VoxCPM2 /
Dia2 `apache-2.0`, Ming `mit`, Fish S2 Pro `other`) [verified]. The Chatterbox retirement and the
VibeVoice takedown come from the research agent's reading of those repos. Size and V100 notes come from
the cards, and are [measured] only where §6.1 says so.

### 6.1 Local runs on one Tesla V100 32 GB [measured]

Five models chosen from the research above: the two with native timestamps (Kokoro, Kyutai),
the open model ranked highest on AA that fits (Ming-3.0-tts, open #3), and two with
prompt-designed voices (Qwen3-TTS, VoxCPM2). All five ran. Times are for the second text
after warm-up, including model-side text splitting.

| # | Model | Precision on V100 | Peak VRAM | Gen time / audio | Notes |
|---|---|---|---:|---|---|
| 60–61 | Kokoro-82M (`am_michael`, `af_heart`) | fp32 default | 0.98 GiB | 0.25 s / 23–25 s (~0.01× real time) | needed the spaCy `en_core_web_sm` wheel from Hugging Face (raw.githubusercontent.com is unreachable here) |
| 62–63 | Kyutai TTS 1.6B (`expresso/ex03-ex01_calm…`, `unmute-prod-website/ex04_narration_longform…`) | **fp32** (loader defaults to bf16; passed `dtype=torch.float32`) | 7.6 GiB | 14–17 s / 22–26 s (~0.65×) | `moshi 0.2.13`; word timings from `TTSResult.all_transcripts`, seconds = step / 12.5 (no acoustic-delay correction needed; see §8) |
| 64–65 | Qwen3-TTS-12Hz-1.7B CustomVoice (Aiden + instruct) / VoiceDesign | fp16 + SDPA | 4.5 GiB | 43–64 s / 20–25 s (~2.2–2.5×) | slow without flash-attn ("manual PyTorch version"); `qwen-tts` package |
| 66–67 | Ming-3.0-tts-0.5B (`UK_George` / freeform narrator prompt) | bf16 as shipped (emulated on Volta, ran fine) | 2.9 GiB | 49–75 s / 18–24 s (~2.3–3.4×) | own venv: `torch 2.6.0+cu126`, `transformers 4.46.3`; splits text into short fragments and sometimes drops the space between sentences ("inside.Each") |
| 68–69 | VoxCPM2 (designed male / female narrator) | **fp32** (forced; checkpoint is bf16), `torch.compile` off | 10.4 GiB | 26–33 s / 20–22 s (~1.2–1.6×) | 48 kHz output; voice description goes in parentheses before the text |

Install recipe (reproducible): conda env `tts_bench_env` (Python 3.11) with
`torch==2.8.0+cu126` from the PyTorch cu126 index (arch list includes `sm_70`), then
`uv venv` per family under `tts_bench_env/venvs/{kyutai,qwen3,ming,voxcpm}`, with
`HF_HOME` pointed at the bench cache. faster-whisper needs
`LD_LIBRARY_PATH` pointing at the pip `nvidia/cublas/lib` and `nvidia/cudnn/lib`.

Not run: CosyVoice 3, MOSS-TTS, IndexTTS-2.5 and Fish S2 Pro need a reference clip for an
English voice (no English presets), and Fish S2 Pro is non-commercial. Dia2 targets dialogue
and wants CUDA 12.8 wheels, which dropped Volta. Fish Drama 3 needs 48 GB or more.

## 7. What switching would change in our pipeline

Today: `tts_openrouter.py` synthesizes one request per `tts.chunk_by` group, bakes each
chunk's `pause_after` as real silence, prepends `head_silence`, and writes `narration.mp3`;
`align_words.py` then sends the whole mp3 to OpenRouter Whisper (`whisper-large-v3`,
`verbose_json`) and matches cue words against the transcript, with a number-word table, US/UK
spelling pairs and edit-distance fallback to survive Whisper's rewrites
(`skills/manim-explain/scripts/`).

**Policy conflict first.** `references/tts-stt.md` says "OpenRouter is the **only** TTS path …
Do not add or restore another vendor." Every option with native timestamps (ElevenLabs direct,
xAI direct, Speechify, Cartesia, Inworld, Fish, MiniMax, or a local Kokoro/Kyutai) breaks that
rule, because OpenRouter returns audio only. Switching models *inside* OpenRouter keeps the
rule but keeps Whisper too. Ben has to choose which rule wins.

**Timestamps (drop the Whisper pass).**
- Per chunk, the provider returns timings relative to that chunk. Absolute time =
  `head_silence + Σ(previous chunk durations + their pause_after)`. Chunk durations come from
  the decoded audio, so this is exact, with no ASR drift [inferred: from how `concat_mp3` builds
  the file].
- Character-level providers (ElevenLabs `alignment`, xAI `graph_times`) need a small
  characters→words fold (split on whitespace, word start = first char start, end = last char
  end). Word-level providers (Speechify `speech_marks`, Cartesia `word_timestamps`, Inworld
  `wordAlignment`, MiniMax `subtitle_type: "word"`, Kokoro tokens, Kyutai `all_transcripts`)
  need none.
- The timings refer to **our own text**, so `align_words.py`'s Whisper-repair layer (number
  words ↔ numerals, British ↔ US spelling, fuzzy matching) becomes unnecessary; cue matching
  becomes an index lookup. ElevenLabs also returns `normalized_alignment` when it expands
  numbers itself; we should use `alignment` (the original text).
- Accuracy: §8 compares native timings with Whisper on the same audio for Kokoro and Kyutai
  [measured]. Hosted native timings could not be measured without keys.

**Pause control.**
- Today pauses exist only *between* chunks (baked silence); inside a chunk, `[pause]` becomes
  "..." and the model decides. That forces extra chunk splits just to get a breath.
- Inline pause syntax by provider: Cartesia `<break time="0.6s"/>`, Speechify / Azure SSML
  `<break>`, Inworld `<break/>`, MiniMax `<#0.6#>`, xAI `[pause]` / `[long-pause]`, Gemini
  `<short pause>` / `<long pause>`, Fish `[pause]`. **ElevenLabs v3/v4 have no break tag**
  (punctuation and dashes only), so with ElevenLabs we keep chunk-baked silence for exact
  pauses [verified: provider docs in §5].
- With native timestamps, a pause made by a tag is visible in the timings, so the beat
  timeline stays exact even when pauses live inside one request.

**Chunking and prosody continuity.**
- Per-chunk synthesis resets prosody at every chunk boundary; our current code passes no
  context. ElevenLabs takes `previous_text` / `next_text` (or `previous_request_ids`) to carry
  intonation across chunks; Cartesia and Inworld WebSockets keep a context id across messages
  [verified: ElevenLabs with-timestamps page; Cartesia/Inworld docs in §5]. Worth wiring in
  whichever provider wins.
- Request limits that bind: Inworld 2,000 chars (sync), Seed 3,000, Polly 3,000; others are
  ≥ 10,000, so whole-script requests are possible but lose our per-chunk retry granularity.

**Speed.**
- Our scripts set `speed: 0.95` for Grok. Through OpenRouter it does nothing: Grok publishes no
  speed range there, and leo at speed 0.75, 0.95 and 1.0 gave 20.86 s, 20.21 s and 20.21 s for
  the same text [measured]. If we want slower or faster narration on Grok, the direct xAI API
  (0.7–1.5) or `<slow>` tags are the levers.
- Our measured narration is already below the reference pace (§8), so the target is usually
  *faster*, not slower.

**Cost** (10-minute video ≈ 10,500 characters; regenerating a script 5–10 times while
iterating multiplies this) [inferred: from §5 prices]:

| Option | Per 10-min video | Notes |
|---|---:|---|
| Grok (today, OpenRouter) | $0.16 | |
| Gemini 3.8 Flash TTS | $0.14 → $0.28 from 2027 | OpenRouter or `GEMINI_API_KEY` |
| Speechify Simba 3.5 | $0.12 (OpenRouter) | direct needs a $10/mo plan |
| Inworld TTS-2 | $0.26 | direct only |
| Fish S2.1 Pro | $0.16 | |
| ElevenLabs v4 | $0.84 | v4 Turbo $0.42 |
| Cartesia Sonic 3.6 | $0.40–0.68 + plan | direct only |
| MiniMax 2.8 HD | $1.05 | direct only |
| Local Kokoro / Kyutai | GPU time only | Kyutai ≈ 0.65 × real time on a V100 in fp32 [measured] |

None of these costs matters next to iteration time; quality and timestamps should decide.

## 8. Method and measurements

**Samples.** Both bench texts (t1 = the existing Nernst narration, 53 words; t2 = the flowing
explainer text, 64 words) for every model, saved as
`research_cache/tts-samples/NN_<provider>_<model>_<voice>_t{1,2}.mp3` and listed in
`research_cache/tts-samples/INDEX.md`. Scripts and raw outputs are in
`research_cache/tts-samples/work/` (`gen_or.py` for OpenRouter, `local_*.py` for local
models, `measure.py`, `ts_jitter.py`, `make_index.py`).

- OpenRouter: default speed (except the Grok baseline at its pipeline value 0.95), `mp3`
  where offered, `pcm` (24 kHz, HeyGen 44.1 kHz) wrapped to wav otherwise. Instruction-capable
  models (Gemini, Fish) got one shared narrator instruction; nothing else was tuned.
- Local: a Python 3.11 env with `torch 2.8.0+cu126`, one uv venv per model family because
  their pins clash (Ming needs `torch 2.6` + `transformers 4.46.3`), and the model weights in
  a Hugging Face cache. One V100, released after each run.
- Loudness: ffmpeg two-pass `loudnorm` to I = -16 LUFS, TP = -1.5 dB, LRA = 11, 44.1 kHz mono mp3.
- **wpm** = script words / voiced span (first to last sample above -45 dB). **Pauses** =
  internal silences of 0.3 s or more. **WER** = local faster-whisper large-v3 (beam 5) transcript
  against the script after lower-casing and stripping punctuation.
- **Native vs Whisper**: for Kokoro and Kyutai, each native word start is matched in order to
  the Whisper word start for the same word in the same file.
- No automatic MOS predictor was run (loading one needed remote code that was not approved), so
  naturalness rests on the arena Elo and Ben's ears.

**Results** (full table in `research_cache/tts-samples/INDEX.md`; raw numbers in
`work/metrics.json`) [measured]:

- **Accuracy:** Whisper recognised every script word in 71 of 74 files. The exceptions:
  Deepgram Flux ("hold" for "hole", one "leaves" dropped), Qwen-Audio 3.0 Plus ("corroded",
  "ion" for "anion"), ElevenLabs Multilingual v2 Brian t1 ("antion"). "Each ion that leaves
  leaves" and "anion" make good stress phrases for future bench texts.
- **Pace:** t1 (short declarative sentences) ran at 131–177 wpm, t2 (flowing) at 113–192.
  Only Speechify Henry (187), VoxCPM2 male (187), Voxtral Oliver / Paul (192 / 184), Fish
  Ethan (184), HeyGen Lucian (183), Ming freeform (179) and Gemini with the brisk prompt (178)
  and ElevenLabs Multilingual v2 Brian (176) reached 175+ on t2. On t1 only HeyGen (177) and
  Ming freeform (176) did. Medians across all samples: 151 (t1) and 161 (t2), well below 3Blue1Brown's 175–200 and close to our
  demos' 139.
- **Pace levers that worked:** a plain-language pace request in Gemini's `instructions`
  (Charon 142→160 on t1, 147→178 on t2). **Levers that did not:** `speed` on Grok through
  OpenRouter (0.75 / 0.95 / 1.0 → 20.86 / 20.21 / 20.21 s for t1); `speed: 1.15` on ElevenLabs
  v3 (t1 140→138, t2 151→161, within run-to-run noise); `speed` on Eleven v4 is rejected
  ("speed is not supported by eleven_v4").
- **Pauses:** the median sample has 6 (t1) / 4 (t2) internal pauses of 0.3 s or more per 20-second text,
  roughly one per sentence break. Kyutai leaves none at all (it runs sentences together),
  and Grok on t2 none either. The arena favourites (ElevenLabs, Gemini) pause at every full
  stop, which partly explains their lower wpm.
- **Native timestamps vs Whisper** (Kokoro and Kyutai; every word matched, 53/53 and 64/64):

  | Sample | Native − Whisper offset (median) | Residual after offset: mean / p95 / max |
  |---|---:|---|
  | Kokoro am_michael t1 / t2 | +0.17 / +0.16 s | 0.09 / 0.25 / 0.32 s · 0.10 / 0.26 / 0.35 s |
  | Kokoro af_heart t1 / t2 | +0.15 / +0.13 s | 0.09 / 0.25 / 0.29 s · 0.09 / 0.20 / 0.32 s |
  | Kyutai ex03calm t1 / t2 | +0.22 / +0.25 s | 0.05 / 0.14 / 0.26 s · 0.06 / 0.15 / 0.19 s |
  | Kyutai ex04narration t1 / t2 | +0.24 / +0.22 s | 0.06 / 0.18 / 0.24 s · 0.05 / 0.16 / 0.24 s |

  Both native sources put word starts 0.13–0.25 s *later* than faster-whisper does, and that
  offset is nearly constant. Once it is removed they agree within about 0.05–0.10 s on average.
  Without a hand-labelled ground truth we can't say which is closer to the true onset
  [inferred]. Kokoro's timings are the durations that drive its own synthesis, and Kyutai's
  come from the text stream emitted with the audio. Either way the jitter is well inside
  the 0–0.3 s tolerance in synthesis.md §4. A fixed offset of this size matters for
  "see-then-hear" leads and should be calibrated once if we switch. Note that our current
  Whisper-based cues may already sit about 0.2 s early relative to these native timings.
- **Cost:** all OpenRouter requests for this bench came to **$0.699** (57 successful, 3 rejected);
  that is the sum of per-generation `total_cost`, and it matches the key's usage delta. Local
  runs used one V100 for about 25 minutes, mostly model downloads and loading.

## 9. Sources

All read 2026-11-21. Web pages were treated as data. Hosted-provider and open-model pages
were read by three research sub-agents; I re-checked the AA leaderboard, the OpenRouter TTS
guide and model list, xAI's voice API, ElevenLabs `with-timestamps`, Inworld and Speechify
timestamps, the Hume docs index, and every open-model licence (Hugging Face API tags).

**OpenRouter**
- TTS guide: <https://openrouter.ai/docs/guides/overview/multimodal/tts>
- Create speech reference: <https://openrouter.ai/docs/api/api-reference/tts/create-speech>
- Speech models API: `GET https://openrouter.ai/api/v1/audio/speech/models`,
  `GET https://openrouter.ai/api/v1/models?output_modalities=speech` (saved in
  `research_cache/tts-samples/work/`)

**Leaderboards**
- Artificial Analysis Speech Arena: <https://artificialanalysis.ai/text-to-speech/leaderboard>
- Artificial Analysis open weights: <https://artificialanalysis.ai/text-to-speech/leaderboard/open-weights>
- TTS Arena V2: <https://huggingface.co/spaces/TTS-AGI/TTS-Arena-V2> (API `https://tts-agi-tts-arena-v2.hf.space/api/leaderboard`)

**Hosted providers**
- ElevenLabs: <https://elevenlabs.io/docs/models>, <https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps>,
  <https://elevenlabs.io/docs/best-practices/prompting/controls>, <https://elevenlabs.io/pricing/api>,
  <https://elevenlabs.io/pricing>, <https://elevenlabs.io/docs/voices/default-voices>, <https://elevenlabs.io/blog/eleven-v4>
- Google: <https://aistudio.google.com/docs/speech-generation>, <https://aistudio.google.com/docs/pricing>,
  <https://aistudio.google.com/docs/models/gemini-3.8-flash-tts>,
  <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/>,
  <https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd>,
  <https://docs.cloud.google.com/text-to-speech/docs/reference/rest/v1beta1/text/synthesize>,
  <https://cloud.google.com/text-to-speech/pricing>
- Microsoft: <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-voices>,
  <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices>,
  <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-speech-synthesis>,
  <https://prices.azure.com/api/retail/prices>
- Speechify: <https://docs.speechify.ai/build/api-reference/v1/audio/stream/with-timestamps>,
  <https://speechify.ai/pricing>, <https://speechify.ai/text-to-speech-api>
- Cartesia: <https://docs.cartesia.ai/api-reference/tts/sse>, <https://docs.cartesia.ai/api-reference/tts/websocket>,
  <https://docs.cartesia.ai/build-with-cartesia/sonic-3/ssml-tags>,
  <https://docs.cartesia.ai/build-with-cartesia/capability-guides/custom-pronunciations>,
  <https://cartesia.ai/pricing>, <https://cartesia.ai/voices/narrator-voice>
- Inworld: <https://docs.inworld.ai/tts/capabilities/timestamps>,
  <https://docs.inworld.ai/api-reference/ttsAPI/texttospeech/synthesize-speech>, <https://inworld.ai/pricing>, <https://inworld.ai/tts>
- Fish Audio: <https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech-stream-with-timestamps>,
  <https://docs.fish.audio/developer-guide/core-features/text-to-speech>,
  <https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits>,
  public voice API `https://api.fish.audio/model/<id>`
- xAI: <https://docs.x.ai/developers/rest-api-reference/inference/voice>, <https://docs.x.ai/developers/model-capabilities/audio/voice>
- MiniMax: <https://platform.minimax.io/docs/api-reference/speech-t2a-http>, <https://platform.minimax.io/docs/guides/pricing-paygo>,
  <https://platform.minimax.io/docs/faq/system-voice-id>
- Mistral: <https://docs.mistral.ai/studio/audio/text-to-speech/generate-speech>
- Deepgram: <https://developers.deepgram.com/docs/flux-tts/feature-overview>, <https://deepgram.com/pricing>
- Rime: <https://docs.rime.ai/docs/websockets>; Murf: <https://murf.ai/api/docs/text-to-speech/web-sockets/advanced-settings>;
  WellSaid: <https://docs.wellsaidlabs.com/reference/using-word-timing-with-the-wellsaid-api>
- OpenAI: <https://developers.openai.com/api/docs/deprecations>, <https://developers.openai.com/api/docs/guides/text-to-speech>
- Amazon Polly: <https://docs.aws.amazon.com/polly/latest/dg/speechmarks.html>, <https://aws.amazon.com/polly/pricing/>
- Shut down: <https://dev.hume.ai/llms.txt>, <https://docs.lmnt.com/build-with-lmnt/word-timestamps>, <https://docs.resemble.ai/>

**Open models**
- Kokoro: <https://huggingface.co/hexgrad/Kokoro-82M>, <https://github.com/hexgrad/kokoro>
- Kyutai TTS: <https://huggingface.co/kyutai/tts-1.6b-en_fr>, <https://github.com/kyutai-labs/delayed-streams-modeling>,
  <https://kyutai.org/next/tts>, voices <https://huggingface.co/kyutai/tts-voices>
- Qwen3-TTS: <https://github.com/QwenLM/Qwen3-TTS>, <https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice>;
  long-form failure study <https://huggingface.co/papers/2609.16989> (via research agent, not re-read)
- Ming-3.0-tts: <https://huggingface.co/inclusionAI/Ming-3.0-tts-0.5B>, <https://github.com/inclusionAI/Ming-3.0-tts>
- VoxCPM2: <https://huggingface.co/openbmb/VoxCPM2>, <https://github.com/OpenBMB/VoxCPM>
- CosyVoice 3: <https://github.com/FunAudioLLM/CosyVoice>; MOSS-TTS: <https://github.com/OpenMOSS/MOSS-TTS>;
  IndexTTS: <https://github.com/index-tts/index-tts>; Dia2: <https://huggingface.co/nari-labs/Dia2-2B>;
  Fish S2 Pro / Drama 3: <https://huggingface.co/fishaudio/s2-pro>, <https://huggingface.co/fishaudio/drama-3>;
  Chatterbox: <https://github.com/resemble-ai/chatterbox>; VibeVoice: <https://github.com/microsoft/VibeVoice>
- PyTorch Volta support: <https://dev-discuss.pytorch.org/t/dropping-volta-support-from-cuda-12-8-binaries-for-release-2-11/3290>

**This repo**
- [synthesis.md §3](synthesis.md#3-language) (pace targets), [styles/landscape.md](styles/landscape.md) (Core Dumped),
  `skills/manim-explain/scripts/tts_openrouter.py`, `align_words.py`, `tts_chunking.py`,
  `skills/manim-explain/references/tts-stt.md`.
