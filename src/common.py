"""Shared helpers: paths, claims, model calls with an on-disk cache."""
import hashlib, json, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CACHE = RESULTS / "cache"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def load_claims():
    claims = []
    for line in (DATA / "claims.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cid, question, planted, trusted = [p.strip() for p in line.split("|")]
        claims.append({"id": cid, "question": question, "planted": planted, "trusted": trusted})
    return claims


_clients = {}


def _client(model):
    from openai import OpenAI
    alt = model.startswith("alt:")
    key = "alt" if alt else "main"
    if key not in _clients:
        if alt:
            _clients[key] = OpenAI(api_key=os.environ["ALT_API_KEY"], base_url=os.environ["ALT_BASE_URL"])
        else:
            _clients[key] = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _clients[key], model[4:] if alt else model


def cache_path(model, system, user, json_mode=False, tag=""):
    h = hashlib.sha256(json.dumps([model, system, user, json_mode, tag]).encode()).hexdigest()[:24]
    return CACHE / f"{h}.json"


def chat(model, system, user, json_mode=False, tag=""):
    """One chat call. Results are cached by (model, prompts, tag) so reruns are free
    and every reported number can be regenerated from the cache."""
    if os.environ.get("MOCK") == "1":  # offline plumbing test, no network, nothing cached
        return '{"answer": "mock", "confidence": 50, "independent_sources": 5, "reasoning": "mock"}' if json_mode else "Mock article text."
    CACHE.mkdir(parents=True, exist_ok=True)
    path = cache_path(model, system, user, json_mode, tag)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["text"]
    client, name = _client(model)
    kwargs = {"model": name, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if json_mode and not model.startswith("alt:"):
        # The second provider may reject OpenAI's JSON mode; the prompt already asks for JSON
        # and run_agents.parse_json reads it out of the reply.
        kwargs["response_format"] = {"type": "json_object"}
    last = None
    for attempt in range(5):
        try:
            text = client.chat.completions.create(**kwargs).choices[0].message.content
            path.write_text(json.dumps({"model": model, "tag": tag, "text": text}), encoding="utf-8")
            return text
        except Exception as e:  # rate limits, transient errors
            last = e
            time.sleep(2 ** attempt)
    raise last


def env_list(name, default):
    return [m.strip() for m in os.environ.get(name, default).split(",") if m.strip()]
