#!/usr/bin/python3
"""tps.py [-h] [NAME=URL ...]: send one short prompt to each OpenAI-compatible endpoint and print tokens/s.
With no arguments the single endpoint $RIG_DRIVER (default http://127.0.0.1:8001) is checked.
Env: RIG_MODEL_NAME (default "local"). Exit status is 1 if any endpoint fails."""
import json, os, sys, time, urllib.request

def ask(url, model, prompt, n=64):
    b = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": n}).encode()
    r = urllib.request.Request(url + "/v1/chat/completions", b, {"Content-Type": "application/json", "Authorization": "Bearer x"})
    t = time.time(); o = json.load(urllib.request.urlopen(r, timeout=600)); dt = time.time() - t
    return o["choices"][0]["message"]["content"], o.get("usage", {}).get("completion_tokens", 0) / dt

def parse(args):
    if not args:
        return [("driver", os.environ.get("RIG_DRIVER", "http://127.0.0.1:8001"))]
    return [tuple(a.split("=", 1)) if "=" in a else (a, a) for a in args]

if __name__ == "__main__":
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__); sys.exit(0)
    ok = True
    for name, url in parse(sys.argv[1:]):
        try:
            txt, tps = ask(url, os.environ.get("RIG_MODEL_NAME", "local"), "Say hello in five words.")
            print(f"{name:12s} OK  {tps:5.1f} tok/s  {txt.strip()[:50]!r}")
        except Exception as e:
            ok = False; print(name, "FAIL", e)
    sys.exit(0 if ok else 1)
