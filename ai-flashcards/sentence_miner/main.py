"""Orchestrator: ties CLI, media, processor, and Anki client together."""
from __future__ import annotations

import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

from cli import check_dependencies, parse_args, ping_anki
from anki_client import AnkiClient, AnkiError
from media_handler import download_audio, slice_audio
from processor import extract_video_id, fetch_transcript, process_transcript

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run() -> int:
    args = parse_args()

    # ── Pre-flight ────────────────────────────────────────────────────────────
    check_dependencies()
    ping_anki(args.anki_url)

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "[ERROR] No Anthropic API key supplied.\n"
            "  Pass --api-key KEY  or  set ANTHROPIC_API_KEY in your environment.",
            file=sys.stderr,
        )
        return 1

    video_id = extract_video_id(args.url)
    log.info("Video ID: %s", video_id)

    # ── Transcript → cards ────────────────────────────────────────────────────
    log.info("Fetching transcript (language=%s) …", args.language)
    segments = fetch_transcript(video_id, args.language)
    log.info("Transcript: %d segments, ~%.0fs total", len(segments), sum(s.get("duration", 0) for s in segments))

    log.info("Extracting vocabulary with %s …", args.model)
    cards = process_transcript(
        segments,
        api_key=api_key,
        model=args.model,
        target_language=args.target_language,
        window=args.window,
        limit=args.limit,
    )

    if not cards:
        log.info("No vocabulary cards found — nothing to add to Anki.")
        return 0

    log.info("Found %d card(s) to create.", len(cards))

    # ── Download audio ────────────────────────────────────────────────────────
    tmp_dir = Path(tempfile.mkdtemp(prefix="sentence_miner_"))
    try:
        log.info("Downloading audio …")
        audio_path = download_audio(args.url, tmp_dir)
        log.info("Audio saved to: %s", audio_path)

        # ── Anki setup ────────────────────────────────────────────────────────
        anki = AnkiClient(args.anki_url)
        anki.ensure_deck(args.deck)
        anki.ensure_note_type(args.note_type)

        added = 0
        skipped = 0

        for i, card in enumerate(cards, 1):
            word: str = card["target_word"]
            sentence: str = card["reconstructed_sentence"]
            definition: str = card["definition"]
            translation: str = card["english_translation"]
            start: float = float(card["start_time"])
            duration: float = float(card["duration"])

            # Ensure duration is at least 0.5s and add a small buffer
            duration = max(duration, 0.5)

            log.info("[%d/%d] %r @ %.2fs + %.2fs", i, len(cards), word, start, duration)

            # Slice audio
            safe_word = "".join(c if c.isalnum() or c in "-_" else "_" for c in word)
            clip_filename = f"sm_{video_id}_{safe_word}_{int(start * 1000)}.m4a"
            clip_path = tmp_dir / clip_filename

            try:
                slice_audio(audio_path, start, duration, clip_path)
            except RuntimeError as exc:
                log.warning("  Skipping (audio slice failed): %s", exc)
                skipped += 1
                continue

            # Store clip in Anki media
            audio_data = clip_path.read_bytes()
            try:
                anki.store_media(clip_filename, audio_data)
            except AnkiError as exc:
                log.warning("  Skipping (media store failed): %s", exc)
                skipped += 1
                continue

            # Add note
            try:
                note_id = anki.add_note(
                    deck=args.deck,
                    note_type=args.note_type,
                    word=word,
                    sentence=sentence,
                    definition=definition,
                    translation=translation,
                    audio_filename=clip_filename,
                )
            except AnkiError as exc:
                log.warning("  Skipping (addNote failed): %s", exc)
                skipped += 1
                continue

            if note_id is None:
                log.info("  Duplicate — skipped.")
                skipped += 1
            else:
                log.info("  Added note #%d", note_id)
                added += 1

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        log.debug("Cleaned up temp dir: %s", tmp_dir)

    log.info("Done.  %d added, %d skipped.", added, skipped)
    return 0


if __name__ == "__main__":
    sys.exit(run())
