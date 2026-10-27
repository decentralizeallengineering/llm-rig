#!/usr/bin/env python3
"""bench.py [-h] [url]: prompt and generation tok/s plus time-to-first-token at ~512 and ~4k prompt tokens, 3 runs each
(medians), then a summarize and a JSON-extraction sanity check. Needs a llama.cpp style server that reports timings.
url defaults to $RIG_DRIVER or http://127.0.0.1:8001."""
import json, os, random, statistics as st, sys, time, urllib.request

if any(a in ("-h", "--help") for a in sys.argv[1:]):
    print(__doc__); sys.exit(0)
U = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("RIG_DRIVER", "http://127.0.0.1:8001")) + "/v1/chat/completions"
MODEL = os.environ.get("RIG_MODEL_NAME", "local")

def call(msg, n):
    b = {"model": MODEL, "messages": [{"role": "user", "content": msg}], "max_tokens": n, "temperature": 0, "stream": True, "cache_prompt": False}
    r = urllib.request.Request(U, json.dumps(b).encode(), {"Content-Type": "application/json"})
    t0 = time.time(); ttft = None; tim = None; txt = ""
    with urllib.request.urlopen(r, timeout=600) as f:
        for line in f:
            line = line.decode().strip()
            if not line.startswith("data: ") or line.endswith("[DONE]"):
                continue
            d = json.loads(line[6:])
            if d.get("timings"):
                tim = d["timings"]
            for c in d.get("choices", []):
                t = c.get("delta", {}).get("content")
                if t:
                    if ttft is None:
                        ttft = time.time() - t0
                    txt += t
    return ttft, tim, txt

def text(nt):
    random.seed(nt)
    w = "alpha river stone cloud engine window garden signal copper violet harbor lantern meadow tunnel orbit pencil".split()
    return " ".join(random.choice(w) for _ in range(int(nt * 0.8)))

if __name__ == "__main__":
    for nt in (512, 4096):
        runs = []
        for i in range(3):
            ttft, tim, _ = call(f"[{i}] Continue this list of words with more words:\n" + text(nt), 128)
            runs.append((tim["prompt_n"], tim["prompt_per_second"], tim["predicted_per_second"], ttft))
        print(f"prompt~{nt} (actual {runs[0][0]} tok): pp {st.median(r[1] for r in runs):.1f} tok/s, "
              f"tg {st.median(r[2] for r in runs):.1f} tok/s, TTFT {st.median(r[3] for r in runs):.2f}s")
    doc = "The team moved the service to a new GPU on Tuesday. Short prompts got faster. Rollback takes one command. Approved by Ann Example; budget 0 dollars; risk: low."
    print("SUMMARY:", call("Summarize in one sentence:\n" + doc, 80)[2])
    j = call("Extract JSON with keys approver,day,budget_usd,risk from the text. Output only JSON.\n" + doc, 80)[2]
    print("JSON:", j)
    try:
        print("JSON valid:", json.loads(j.strip().strip("`").removeprefix("json").strip()))
    except Exception as e:
        print("JSON invalid", e)
