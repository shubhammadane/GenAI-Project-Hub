# Context Squeezer

Middleware that shrinks retrieved (RAG) context before it is sent to an LLM, so you pay for fewer tokens and the model sees denser text.

```
raw context ─► 1. filler removal ─► 2. word scoring ─► 3. sentence budgeting ─► squeezed prompt
               (spaCy + rules)      (surprisal)         (density + question)
```

## Team Members

| Name | Roll Number |
|---|---|
| Siya Dadpe | BT23F05F013 |
| Gayatri Shisode | BT23F05F062 |

## Problem Statement

Retrieval-Augmented Generation (RAG) systems often retrieve more context than an LLM needs. Sending this full context increases token cost and latency, and can bury the relevant information in filler, repetition, and off-topic text.

## Objectives

- Reduce the number of tokens sent to an LLM without losing the information needed to answer a question.
- Preserve important content such as names, numbers, acronyms, identifiers, and negations.
- Rank sentences by information density and relevance to the user's question before pruning words.
- Provide a working demo and an evaluation harness that compare full context with squeezed context.

## Proposed Solution

Context Squeezer processes retrieved passages in three stages:

| Stage | What it does | Code |
|---|---|---|
| 1 | Marks filler phrases ("furthermore", "as previously stated", "in order to" → "to"). With spaCy it also finds sentences, named entities, numbers and negations. | `Source-Code/context_squeezer/linguistic.py` |
| 2 | Scores every word by surprisal (bits). Predictable words are pruned first. Numbers, names, acronyms, identifiers and negations are protected. | `Source-Code/context_squeezer/scorers.py` |
| 3 | Ranks sentences by information density plus relevance to the question, keeps the best until the token budget is met, then prunes words down to it. | `Source-Code/context_squeezer/pipeline.py` |

Every token keeps its position in the original text, so the demo can show exactly what was cut and why.

## Technologies Used

- Python 3
- Flask demo server
- spaCy for sentence segmentation and named-entity recognition
- tiktoken for exact token counting (optional)
- Hugging Face Transformers and PyTorch for language-model scoring (optional)
- HotpotQA for evaluation data
- Any OpenAI-compatible LLM endpoint (Ollama, vLLM, LM Studio, Groq, OpenAI)
- `unittest` for tests

## System Workflow / Architecture

```
Retrieved passages + question
             │
             ▼
   Stage 1: linguistic analysis
   filler removal, sentences, entities,
   numbers, negations
             │
             ▼
   Stage 2: word scoring
   surprisal-based pruning with
   protected-token rules
             │
             ▼
   Stage 3: sentence budgeting
   density + question relevance,
   then word pruning to token budget
             │
             ▼
      Squeezed context ─► LLM
```

The project contains:

```
Source-Code/
├── context_squeezer/   pipeline, linguistic stage, scorers, token counting
├── server.py           Flask demo + JSON API (POST /api/squeeze, /api/compare)
├── static/index.html   demo front end
├── eval/               metrics, HotpotQA loader, readers, baselines, run_eval.py
└── tests/              unit tests
```

## Implementation

### Quick start

```bash
cd Source-Code
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

### Two scorers

- **Heuristic (default, no model).** Word-length and repetition heuristics. Instant, runs anywhere. It is a stand-in, not a language model.
- **Language model (`HFScorer`).** Per-word surprisal from a small causal LM. Install `torch` and `transformers`; the demo then shows a scorer dropdown. Default model is `Qwen/Qwen2.5-0.5B`; set `SQUEEZER_HF_MODEL` (server) or `--hf-model` (eval) to use a 1B-3B Llama/Mistral-class model instead. On CPU it takes roughly 10-20 seconds per question, so the heuristic stays the default.

### Ask the LLM in the demo

The **Ask the LLM** button sends the question twice, once with the full context and once with the squeezed context, then shows both answers with token counts and response times and says whether they match. It reads the same environment variables as the evaluation script:

```bash
export LLM_BASE_URL=http://localhost:11434/v1
export LLM_MODEL=llama3.2:3b
export LLM_API_KEY=...        # only if your endpoint needs one
python server.py
```

On PowerShell use `$env:LLM_BASE_URL = "http://localhost:11434/v1"` and so on. If the endpoint, model or key is missing, the button is disabled and the page says why. The key stays on the server and is never sent to the browser.

## Results / Output

The evaluation harness reports, for the full context, Context Squeezer at several keep ratios, two baselines at the same token budget (truncate, random word drop) and ablations:

- **IRR (Information Recovery Rate)** = mean F1 with squeezed context ÷ mean F1 with full context
- Exact Match, F1, agreement with the full-context answer, token reduction, compression overhead (ms)

Run the evaluation with:

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

**Important:** The bundled sample set is 6 invented questions and its reader is a rule-based script, not an LLM. The results prove the harness runs, nothing more. Do not report them as model results. Without `tiktoken`, token counts are estimates. Without spaCy, names are detected by capitalisation and sentences by regex. Install spaCy and the model for the real Stage 1.

## Screenshots

Demo screenshots are available in the `Screenshots/` folder.

## Demo Files

The `Demo/` folder contains the evaluation output used during the demonstration:

- `proxy_results.csv` — summary table for full context, baselines, and Context Squeezer at different keep ratios
- `proxy_results.json` — full evaluation metadata and raw results

## Future Scope

- Add a full evaluation on HotpotQA with a local or hosted LLM.
- Compare against LLMLingua and LongLLMLingua as additional baselines.
- Improve sentence and word ranking with question-aware embeddings.
- Add support for more document types and multilingual context.
- Package the middleware as a reusable service for existing RAG pipelines.

## References

- Litman et al., *Selective Context: Compressing Context to Enhance Inference Efficiency of Large Language Models* (EMNLP 2023).
- Jiang et al., *LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models* (EMNLP 2023).
- Jiang et al., *LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression* (2023).
- Pan et al., *LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression* (2024).
- Yang et al., *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering* (EMNLP 2018).
- spaCy: Industrial-strength Natural Language Processing in Python.
- Hugging Face Transformers and Qwen models.

## Demo / Deployment Link

Run the demo locally with `python server.py` from the `Source-Code/` folder and open `http://127.0.0.1:8000`. A hosted demo link will be added here if deployed.
