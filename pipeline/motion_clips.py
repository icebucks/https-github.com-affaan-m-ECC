#!/usr/bin/env python3
"""Echte Bewegung: macht aus einem realistischen Szenenbild einen kurzen Videoclip (Bild-zu-Video).

Anbieter (der Reihe nach, der erste, der klappt, gewinnt):
  1. Wan 2.2 über HuggingFace ZeroGPU (Token des Nutzers wird vom Netzwerk-Proxy eingesetzt;
     mit HuggingFace PRO ca. 15–20 Clips/Tag)
Klappt nichts (kein Kontingent), bleibt die Szene beim 2.5D-Kamera-Modus – das Video scheitert nie daran.

Aufruf: python3 motion_clips.py <request.json>
request = { "out_dir": "...", "items": [ { "key": "m-…", "image": ".../b-….jpg", "prompt": "…", "seed": 7 } ] }
Ergebnis: <out_dir>/<key>.mp4 je erfolgreichem Clip; Zusammenfassung als JSON auf stdout.
"""
import json
import os
import shutil
import sys
import time

NEG = ("static, still image, frozen, deformed, disfigured, extra fingers, extra limbs, bad hands, blurry, "
       "text, watermark, modern clothing, morphing, flicker")
WAN = "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space"


def wan(client, image, prompt, seed):
    from gradio_client import handle_file
    r = client.predict(handle_file(image), prompt, 6, NEG, 3.5, 1, 1, int(seed), False, api_name="/generate_video")
    return r[0]["video"] if isinstance(r[0], dict) else r[0]


def main():
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    out = req["out_dir"]
    os.makedirs(out, exist_ok=True)
    done, failed = [], []
    todo = [it for it in req["items"] if not os.path.exists(os.path.join(out, it["key"] + ".mp4"))]
    done += [it["key"] for it in req["items"] if it not in todo]
    client = None
    quota_gone = False
    for it in todo:
        if quota_gone:
            failed.append({"key": it["key"], "grund": "Kontingent erschöpft"})
            continue
        t = time.time()
        try:
            if client is None:
                from gradio_client import Client
                client = Client(WAN, verbose=False, headers={"Authorization": "Bearer proxy-injected"})
            path = wan(client, it["image"], it["prompt"], it.get("seed", 7))
            shutil.copy(path, os.path.join(out, it["key"] + ".mp4"))
            done.append(it["key"])
            print(f"  Bewegung {it['key']} ({time.time() - t:.0f} s)", file=sys.stderr, flush=True)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "quota" in msg.lower() or "limit" in msg.lower():
                quota_gone = True
            failed.append({"key": it["key"], "grund": msg[:200]})
            print(f"  Bewegung {it['key']} nicht möglich → 2.5D ({msg[:120]})", file=sys.stderr, flush=True)
    print(json.dumps({"done": done, "failed": failed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
