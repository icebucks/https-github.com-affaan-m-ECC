#!/usr/bin/env python3
"""Realistische Szenenbilder (RealVisXL V5 Lightning, lokal, OpenRAIL++) + Tiefenkarten
(Depth Anything V2 Small, Apache 2.0) für die 2.5D-Kamerafahrten.

Aufruf: python3 scene_images.py <request.json>
request = { "out_dir": "assets/<id>/bilder", "items": [ { "key": "s01-ab12cd", "prompt": "...", "seed": 7 }, ... ],
            "negative": "...", "width": 768, "height": 1344, "steps": 6 }
Ergebnis je Bild: <key>.jpg und <key>_depth.png (hell = nah). Vorhandene Dateien werden nicht neu erzeugt (Cache).
"""
import json
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402

NEG = ("cartoon, painting, illustration, anime, 3d render, deformed, disfigured, extra fingers, extra limbs, bad hands, "
       "bad anatomy, blurry, lowres, text, letters, watermark, logo, frame, modern clothing, modern objects")


def main():
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    out = req["out_dir"]
    os.makedirs(out, exist_ok=True)
    todo = [it for it in req["items"] if not os.path.exists(os.path.join(out, it["key"] + ".jpg"))]
    torch.set_num_threads(int(os.environ.get("IMG_THREADS", "4")))
    if todo:
        from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLPipeline
        pipe = StableDiffusionXLPipeline.from_pretrained("SG161222/RealVisXL_V5.0_Lightning", torch_dtype=torch.bfloat16,
                                                         variant="fp16", use_safetensors=True)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type="sde-dpmsolver++",
                                                                 use_karras_sigmas=True)
        for i, it in enumerate(todo):
            t = time.time()
            img = pipe(it["prompt"], negative_prompt=req.get("negative") or NEG, width=req.get("width", 768),
                       height=req.get("height", 1344), num_inference_steps=req.get("steps", 6), guidance_scale=1.5,
                       generator=torch.Generator().manual_seed(int(it.get("seed", 7)))).images[0]
            img.save(os.path.join(out, it["key"] + ".jpg"), quality=93)
            print(f"  Bild {i + 1}/{len(todo)} {it['key']} ({time.time() - t:.0f} s)", file=sys.stderr, flush=True)
        del pipe
    # Schärfen: Real-ESRGAN x2 (BSD-3), dann auf 1152 px Breite (genug Reserve für Kamerazoom bei 1080 px)
    esr = os.path.join(os.environ.get("HOME", "/root"), ".cache", "ich-war-dabei", "models", "RealESRGAN_x2plus.pth")
    small = [it for it in req["items"] if Image.open(os.path.join(out, it["key"] + ".jpg")).width < 1000]
    if small and os.path.exists(esr):
        from spandrel import ModelLoader
        up = ModelLoader().load_from_file(esr).eval()
        for it in small:
            t = time.time()
            f = os.path.join(out, it["key"] + ".jpg")
            img = Image.open(f).convert("RGB")
            x = torch.from_numpy(np.array(img)).permute(2, 0, 1).float().unsqueeze(0) / 255
            _, _, H, W = x.shape
            res = torch.zeros(1, 3, H * 2, W * 2)
            T, P = 384, 16  # Kacheln mit Überlappung (keine Nähte)
            with torch.no_grad():
                for y in range(0, H, T):
                    for x0 in range(0, W, T):
                        y0, y1 = max(0, y - P), min(H, y + T + P)
                        a0, a1 = max(0, x0 - P), min(W, x0 + T + P)
                        o = up(x[:, :, y0:y1, a0:a1])
                        oy, ox = (y - y0) * 2, (x0 - a0) * 2
                        hh, ww = min(T, H - y) * 2, min(T, W - x0) * 2
                        res[:, :, y * 2:y * 2 + hh, x0 * 2:x0 * 2 + ww] = o[:, :, oy:oy + hh, ox:ox + ww]
            arr = (res.clamp(0, 1)[0].permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            big = Image.fromarray(arr).resize((1152, int(1152 * H / W)), Image.LANCZOS)
            big.save(f, quality=93)
            print(f"  Schärfen {it['key']} ({time.time() - t:.0f} s)", file=sys.stderr, flush=True)
        del up
    elif small:
        print("  Hinweis: Real-ESRGAN-Modell fehlt (npm run setup) – Bilder bleiben ungeschärft", file=sys.stderr)
    # Tiefenkarten
    need = [it for it in req["items"] if not os.path.exists(os.path.join(out, it["key"] + "_depth.png"))]
    if need:
        from transformers import pipeline
        dep = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
        for it in need:
            img = Image.open(os.path.join(out, it["key"] + ".jpg")).convert("RGB")
            d = dep(img)["predicted_depth"]
            d = d.squeeze().float().numpy()
            d = (d - d.min()) / (np.ptp(d) + 1e-6)
            dimg = Image.fromarray((d * 255).astype(np.uint8)).resize(img.size, Image.BICUBIC)
            # weichzeichnen: verhindert Risse an Kanten beim Verschieben
            dimg = dimg.filter(ImageFilter.GaussianBlur(radius=6))
            dimg.save(os.path.join(out, it["key"] + "_depth.png"))
            print(f"  Tiefe {it['key']}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
