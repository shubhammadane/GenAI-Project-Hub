"""Demo server: python server.py  ->  http://127.0.0.1:8000

Environment variables
    SQUEEZER_HF_MODEL   model for the "language model" scorer (default Qwen/Qwen2.5-0.5B)
    LLM_BASE_URL        OpenAI-compatible endpoint for POST /api/compare
    LLM_MODEL           model name for POST /api/compare
    LLM_API_KEY         key for that endpoint; never sent to the browser
    PORT / HOST         where to listen (default 127.0.0.1:8000)
"""
from __future__ import annotations

import importlib.util
import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from context_squeezer import HeuristicScorer, SqueezeConfig, Squeezer
from context_squeezer.linguistic import Analyzer
from context_squeezer.tokens import count_tokens, tokenizer_name
from eval.metrics import normalize_answer
from eval.readers import llm_status

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

MAX_CHARS = 200_000
_analyzer = Analyzer()
_squeezers: dict[str, Squeezer] = {}
_readers: dict[str, object] = {}
_lock = threading.Lock()


def hf_available() -> bool:
    return importlib.util.find_spec("torch") is not None and importlib.util.find_spec("transformers") is not None


def get_squeezer(kind: str) -> Squeezer:
    with _lock:
        if kind not in _squeezers:
            if kind == "hf":
                from context_squeezer import HFScorer

                scorer = HFScorer(os.environ.get("SQUEEZER_HF_MODEL", "Qwen/Qwen2.5-0.5B"))
            else:
                scorer = HeuristicScorer()
            _squeezers[kind] = Squeezer(scorer=scorer, analyzer=_analyzer)
        return _squeezers[kind]


def get_reader():
    with _lock:
        if "reader" not in _readers:
            from eval.readers import OpenAICompatReader, env_reader_config

            base_url, model, _ = env_reader_config()
            _readers["reader"] = OpenAICompatReader(base_url, model)
        return _readers["reader"]


def _safe_error(message: str) -> str:
    key = os.environ.get("LLM_API_KEY", "")
    return message.replace(key, "***") if key else message


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/info")
def info():
    return jsonify(parser=_analyzer.backend, tokenizer=tokenizer_name(), scorers={
        "heuristic": "Word heuristic (no model, instant)",
        **({"hf": "Small language model (slower, closer to the proposal)"} if hf_available() else {}),
    }, llm=llm_status())


@app.post("/api/squeeze")
def squeeze():
    body = request.get_json(silent=True) or {}
    context = body.get("context", "")
    if not isinstance(context, str) or not context.strip():
        return jsonify(error="Paste some text to squeeze."), 400
    if len(context) > MAX_CHARS:
        return jsonify(error=f"Text is too long for the demo ({len(context):,} characters). Limit: {MAX_CHARS:,}."), 413
    kind = body.get("scorer", "heuristic")
    if kind == "hf" and not hf_available():
        return jsonify(error="The language-model scorer needs torch and transformers installed."), 400
    try:
        cfg = SqueezeConfig(
            keep_ratio=float(body.get("keep_ratio", 0.4)),
            use_filter=bool(body.get("use_filter", True)),
            use_word_pruning=bool(body.get("use_word_pruning", True)),
            use_sentence_ranking=bool(body.get("use_sentence_ranking", True)),
        )
        question = body.get("question") or None
        t = time.perf_counter()
        result = get_squeezer(kind if kind in ("heuristic", "hf") else "heuristic").squeeze(
            context, question=question, config=cfg)
    except (TypeError, ValueError) as e:
        return jsonify(error=f"Invalid setting: {e}"), 400
    out = result.to_dict()
    out["elapsed_ms"] = round((time.perf_counter() - t) * 1000, 1)
    return jsonify(out)


@app.post("/api/compare")
def compare():
    status = llm_status()
    if not status["available"]:
        return jsonify(error=status["reason"]), 503

    body = request.get_json(silent=True) or {}
    context = body.get("context", "")
    question = (body.get("question") or "").strip()
    if not isinstance(context, str) or not context.strip():
        return jsonify(error="Paste some text to compare."), 400
    if not question:
        return jsonify(error="Type a question so the model knows what to answer."), 400
    if len(context) > MAX_CHARS:
        return jsonify(error=f"Text is too long for the demo ({len(context):,} characters). Limit: {MAX_CHARS:,}."), 413

    kind = body.get("scorer", "heuristic")
    if kind == "hf" and not hf_available():
        return jsonify(error="The language-model scorer needs torch and transformers installed."), 400
    try:
        ratio = float(body.get("keep_ratio", 0.4))
        t = time.perf_counter()
        result = get_squeezer(kind if kind in ("heuristic", "hf") else "heuristic").squeeze(
            context, question=question, config=SqueezeConfig(keep_ratio=ratio))
        squeeze_ms = (time.perf_counter() - t) * 1000

        reader = get_reader()
        t = time.perf_counter()
        full_answer = reader.answer(question, context)
        full_ms = (time.perf_counter() - t) * 1000
        t = time.perf_counter()
        squeezed_answer = reader.answer(question, result.squeezed)
        squeezed_ms = (time.perf_counter() - t) * 1000
    except (TypeError, ValueError) as e:
        return jsonify(error=f"Invalid setting: {e}"), 400
    except Exception as e:  # reader/network failures must not crash the demo
        return jsonify(error=_safe_error(f"The language model call failed: {e}")), 502

    return jsonify(
        full={"answer": full_answer, "tokens": count_tokens(context), "ms": round(full_ms, 1)},
        squeezed={"answer": squeezed_answer, "tokens": count_tokens(result.squeezed),
                  "ms": round(squeezed_ms, 1)},
        match=normalize_answer(full_answer) == normalize_answer(squeezed_answer),
        keep_ratio=result.keep_ratio,
        reduction=result.reduction,
        squeeze_ms=round(squeeze_ms, 1),
        tokenizer=tokenizer_name(),
    )


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")), debug=False)
