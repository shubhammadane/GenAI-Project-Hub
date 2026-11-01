"""Stage 1: linguistic analysis and filler removal.

Every piece of text is split into tokens that keep their character offsets in
the original string. Later stages only change the `status` of a token, so the
demo can show exactly what was cut and where.

spaCy is used when it is installed (sentence boundaries, named entities, POS,
negation, interjections). Without spaCy, or without a trained model, regex
rules and word lists take over. `Analyzer.backend` says which one is active.
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass

TOKEN_RE = re.compile(
    r"[$€£₹]?\d+(?:[,.:/-]\d+)*%?[A-Za-z]*"
    r"|\w+(?:[-'’./]\w+)*"
    r"|[^\w\s]",
    re.UNICODE,
)

STOPWORDS = frozenset(
    """a an the and or but if of at by for with about against between into through during before after
    above below to from up down in out on off over under again further then once here there when where why how
    all any both each few more most other some such no nor not only own same so than too very can will just
    should now is are was were be been being have has had having do does did doing i me my we our you your he him
    his she her it its they them their what which who whom this that these those am would could may might must
    shall also as while because until s t""".split()
)

# Words that change meaning when removed; never pruned in Stage 2.
NEGATIONS = frozenset(
    "not no never none nor without cannot neither nobody nothing except unless only n't".split()
)
KEEP_WORDS = NEGATIONS | frozenset("must than before after because if".split())

ABBREVIATIONS = frozenset(
    "dr mr mrs ms prof st vs etc e.g i.e inc ltd no fig approx dept est jr sr".split()
)

FILLER_PHRASES = [
    "as previously stated", "as previously mentioned", "as previously noted", "as mentioned earlier",
    "as mentioned above", "as noted above", "as stated above", "as discussed earlier", "as we can see",
    "as you can see", "it is worth noting that", "it is worth mentioning that", "it should be noted that",
    "it is important to note that", "it is important to remember that", "it is interesting to note that",
    "please note that", "needless to say", "it goes without saying that", "at the end of the day",
    "in my opinion", "to be honest", "to be fair", "as a matter of fact", "in fact", "by the way",
    "that being said", "having said that", "with that said", "first and foremost", "in addition",
    "in conclusion", "in a nutshell", "all in all", "generally speaking", "in other words",
    "that is to say", "of course", "in order to", "so as to", "as such",
    "furthermore", "moreover", "additionally", "basically", "essentially", "actually", "really",
    "very", "quite", "simply", "obviously", "clearly", "certainly", "definitely", "literally",
    "honestly", "frankly", "indeed", "anyway",
]
# "in order to" -> "to": keep the last word of the phrase.
KEEP_LAST = {"in order to": 1, "so as to": 1}

_FILLER_RE = re.compile(
    r"(?<!\w)(?:"
    + "|".join(r"\s+".join(map(re.escape, p.split())) for p in sorted(FILLER_PHRASES, key=len, reverse=True))
    + r")(?!\w)",
    re.IGNORECASE,
)

_FUNC_POS = {"DET", "ADP", "PART", "CCONJ", "SCONJ", "AUX", "PRON", "INTJ"}


@dataclass
class Tok:
    i: int
    text: str
    start: int
    end: int
    kind: str  # "word" or "punct"
    sent: int = 0
    para: int = 0
    protected: bool = False
    func: bool = False
    discourse: bool = False
    status: str = "kept"  # kept | filler | entropy | sentence | punct
    surprisal: float = 0.0


@dataclass
class Sent:
    start: int
    end: int
    para: int


def _paragraph_starts(text: str) -> list[int]:
    starts = [0]
    for m in re.finditer(r"\n\s*\n", text):
        starts.append(m.end())
    return starts


def regex_sentences(text: str) -> list[tuple[int, int]]:
    """Rule-based sentence splitter that respects blank lines and common abbreviations."""
    spans: list[tuple[int, int]] = []
    for pm in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", text):
        ptxt = pm.group()
        base = pm.start()
        pos = 0
        for m in re.finditer(r"[.!?][\"')\]]*\s+", ptxt):
            before = re.search(r"([\w.]+)$", ptxt[: m.start()])
            if before:
                w = before.group(1).lower()
                if w in ABBREVIATIONS or (len(w) == 1 and w.isalpha()):
                    continue
            nxt = ptxt[m.end(): m.end() + 1]
            if nxt and not re.match(r"[A-Z0-9\"'(\[]", nxt):
                continue
            end = m.start() + len(m.group().rstrip())
            spans.append((base + pos, base + end))
            pos = m.end()
        if pos < len(ptxt.rstrip()):
            spans.append((base + pos, base + len(ptxt.rstrip())))
    return spans


class Analyzer:
    def __init__(self, use_spacy: bool = True, model: str = "en_core_web_sm"):
        self.nlp = None
        self.has_tagger = False
        self.backend = "regex-fallback"
        if use_spacy:
            try:
                import spacy

                try:
                    self.nlp = spacy.load(model)
                    self.has_tagger = True
                    self.backend = f"spacy:{model}"
                except OSError:
                    self.nlp = spacy.blank("en")
                    self.nlp.add_pipe("sentencizer")
                    self.backend = "spacy:blank+heuristics (run: python -m spacy download en_core_web_sm)"
            except ImportError:
                pass

    # ------------------------------------------------------------------
    def analyze(self, text: str) -> tuple[list[Tok], list[Sent]]:
        para_starts = _paragraph_starts(text)
        doc = None
        if self.nlp is not None and text.strip():
            self.nlp.max_length = max(self.nlp.max_length, len(text) + 1000)
            doc = self.nlp(text)
            sent_spans = [(s.start_char, s.end_char) for s in doc.sents if s.text.strip()]
        else:
            sent_spans = regex_sentences(text)
        sents = [Sent(a, b, bisect.bisect_right(para_starts, a) - 1) for a, b in sent_spans]
        sent_starts = [s.start for s in sents]

        toks: list[Tok] = []
        for m in TOKEN_RE.finditer(text):
            t = m.group()
            kind = "punct" if (len(t) == 1 and not t.isalnum()) else "word"
            tok = Tok(len(toks), t, m.start(), m.end(), kind)
            tok.sent = max(0, bisect.bisect_right(sent_starts, tok.start) - 1) if sents else 0
            tok.para = bisect.bisect_right(para_starts, tok.start) - 1
            toks.append(tok)

        self._flag(toks, doc)
        return toks, sents

    # ------------------------------------------------------------------
    def _flag(self, toks: list[Tok], doc) -> None:
        seen_sent: set[int] = set()
        sp_starts = [t.idx for t in doc] if (doc is not None and self.has_tagger) else None
        for tok in toks:
            if tok.kind != "word":
                continue
            low = tok.text.lower()
            first_in_sentence = tok.sent not in seen_sent
            seen_sent.add(tok.sent)

            func = low in STOPWORDS
            prot = low in KEEP_WORDS or low.endswith("n't")
            if any(c.isdigit() for c in tok.text) or tok.text[0] in "$€£₹":
                prot = True
            elif tok.text.isupper() and len(tok.text) >= 2 and tok.text.isalpha():
                prot = True  # acronyms
            elif re.search(r"[a-z][A-Z]|[_@/]|\w\.\w", tok.text):
                prot = True  # camelCase, identifiers, urls, versions
            elif sp_starts is None and tok.text[0].isupper() and not first_in_sentence and low not in STOPWORDS:
                prot = True  # capitalised mid-sentence: likely a name

            if sp_starts is not None:
                st = doc[max(0, bisect.bisect_right(sp_starts, tok.start) - 1)]
                if st.ent_type_ or st.pos_ in ("PROPN", "NUM") or st.dep_ == "neg":
                    prot = True
                func = st.pos_ in _FUNC_POS
                if st.pos_ == "INTJ" or st.dep_ == "discourse":
                    tok.discourse = True
            tok.protected = prot
            tok.func = func and not prot


def mark_fillers(text: str, toks: list[Tok]) -> int:
    """Stage 1: mark filler phrases and discourse words as dropped. Returns number of tokens marked."""
    starts = [t.start for t in toks]
    marked = 0
    for m in _FILLER_RE.finditer(text):
        key = re.sub(r"\s+", " ", m.group().lower())
        keep_last = KEEP_LAST.get(key, 0)
        lo = bisect.bisect_left(starts, m.start())
        hi = bisect.bisect_left(starts, m.end())
        span = [t for t in toks[lo:hi] if t.end <= m.end()]
        words = [t for t in span if t.kind == "word"]
        drop = words[: len(words) - keep_last] if keep_last else words
        for t in drop:
            if t.status == "kept" and not any(c.isdigit() for c in t.text):
                t.status = "filler"
                marked += 1
        if drop and not keep_last and span:
            nxt = span[-1].i + 1
            if nxt < len(toks) and toks[nxt].text == "," and toks[nxt].start == span[-1].end:
                toks[nxt].status = "filler"
                marked += 1
    for t in toks:
        if t.discourse and t.status == "kept" and not t.protected:
            t.status = "filler"
            marked += 1
    return marked
