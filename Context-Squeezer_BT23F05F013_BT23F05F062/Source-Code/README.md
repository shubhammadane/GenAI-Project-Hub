# Context Squeezer

Middleware that shrinks retrieved (RAG) context before it is sent to an LLM, so you pay for fewer tokens and the model sees denser text.

```
raw context ─► 1. filler removal ─► 2. word scoring ─► 3. sentence budgeting ─► squeezed prompt
               (spaCy + rules)      (surprisal)         (density + question)
```

| Stage | What it does | Code |
|---|---|---|
| 1 | Marks filler phrases ("furthermore", "as previously stated", "in order to" → "to"). With spaCy it also finds sentences, named entities, numbers and negations. | `context_squeezer/linguistic.py` |
| 2 | Scores every word by surprisal (bits). Predictable words are pruned first. Numbers, names, acronyms, identifiers and negations are protected. | `context_squeezer/scorers.py` |
| 3 | Ranks sentences by information density plus relevance to the question, keeps the best until the token budget is met, then prunes words down to it. | `context_squeezer/pipeline.py` |

Every token keeps its position in the original text, so the demo can show exactly what was cut and why.

## Quick start

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm

python server.py                 # demo at http://127.0.0.1:8000
python -m unittest discover -s tests -v
```

Use it from Python:

```python
from context_squeezer import Squeezer, SqueezeConfig

sq = Squeezer()
res = sq.squeeze(passages, question="How many days do I have to ask for a refund?",
                 config=SqueezeConfig(keep_ratio=0.4))   # keep 40% of the tokens
print(res.squeezed, res.original_tokens, "->", res.squeezed_tokens)
```

## Two scorers

* **Heuristic (default, no model).** Word-length and repetition heuristics. Instant, runs anywhere. It is a stand-in, not a language model.
* **Language model (`HFScorer`).** Per-word surprisal from a small causal LM. Install `torch` and `transformers`; the demo then shows a scorer dropdown. Default model is `Qwen/Qwen2.5-0.5B`; set `SQUEEZER_HF_MODEL` (server) or `--hf-model` (eval) to use a 1B-3B Llama/Mistral-class model instead. On CPU it takes roughly 10-20 seconds per question, so the heuristic stays the default.

## Ask the LLM in the demo

The **Ask the LLM** button sends the question twice, once with the full context and once with the squeezed context, then shows both answers with token counts and response times and says whether they match. It reads the same environment variables as the evaluation script:

```bash
export LLM_BASE_URL=http://localhost:11434/v1
export LLM_MODEL=llama3.2:3b
export LLM_API_KEY=...        # only if your endpoint needs one
python server.py
```

On PowerShell use `$env:LLM_BASE_URL = "http://localhost:11434/v1"` and so on. If the endpoint, model or key is missing, the button is disabled and the page says why. The key stays on the server and is never sent to the browser.

## Evaluation

```bash
# 1. Smoke test: 6 synthetic questions + a rule-based reader (no downloads, no API)
python -m eval.run_eval

# 2. Real evaluation: HotpotQA (distractor setting) + a local or hosted LLM
python -m eval.run_eval --data hotpot_dev_distractor_v1.json --limit 300 \
    --reader openai --base-url http://localhost:11434/v1 --model llama3.2:3b \
    --scorer hf --hf-model Qwen/Qwen2.5-0.5B
```

`--reader openai` works with any OpenAI-compatible endpoint (Ollama, vLLM, LM Studio, Groq, OpenAI). Put the key in `LLM_API_KEY` if needed. Answers are cached in `results/answer_cache.json`, so an interrupted run resumes without repeating calls.

HotpotQA: get `hotpot_dev_distractor_v1.json` from the HotpotQA site (hotpotqa.github.io) or export the `distractor` config from the Hugging Face `hotpotqa/hotpot_qa` dataset. Both formats load.

The table reports, for the full context, Context Squeezer at several keep ratios, two baselines at the same token budget (truncate, random word drop) and ablations:

* **IRR (Information Recovery Rate)** = mean F1 with squeezed context ÷ mean F1 with full context
* Exact Match, F1, agreement with the full-context answer, token reduction, compression overhead (ms)

## Read this before quoting any numbers

* The bundled sample set is **6 invented questions** and its reader is **a rule-based script**, not an LLM. The results prove the harness runs, nothing more. Do not report them.
* Without `tiktoken`, token counts are estimates.
* Without spaCy, names are detected by capitalisation and sentences by regex. Install spaCy and the model for the real Stage 1.
* The idea is close to published work (Selective Context, LLMLingua, LongLLMLingua, LLMLingua-2). Cite them and consider using LLMLingua as an extra baseline.

## Layout

```
context_squeezer/   pipeline, linguistic stage, scorers, token counting
server.py           Flask demo + JSON API (POST /api/squeeze, /api/compare)
static/index.html   demo front end
eval/               metrics, HotpotQA loader, readers, baselines, run_eval.py, sample_data.json
tests/              unit tests
```
