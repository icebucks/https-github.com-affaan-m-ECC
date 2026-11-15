#!/usr/bin/env node
// Einmalige Einrichtung (idempotent): Node-Pakete, Python-Pakete, Stimmen, Chrome für HyperFrames.
//   npm run setup
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const VOICES = process.env.VOICE_DIR || path.join(process.env.HOME || ROOT, ".cache", "ich-war-dabei", "voices");
const run = (cmd, opts = {}) => { console.log(`$ ${cmd}`); execSync(cmd, { stdio: "inherit", cwd: ROOT, ...opts }); };
const has = (cmd) => { try { execSync(`command -v ${cmd}`, { stdio: "ignore" }); return true; } catch { return false; } };

// 1) Node + FFmpeg
const major = Number(process.versions.node.split(".")[0]);
if (major < 22) { console.error(`Node.js ${process.versions.node} ist zu alt – bitte Node 22 oder neuer installieren.`); process.exit(1); }
if (!has("ffmpeg")) {
  if (has("apt-get")) run("apt-get update -qq && apt-get install -y -qq ffmpeg");
  else if (has("brew")) run("brew install ffmpeg");
  else { console.error("FFmpeg fehlt – bitte installieren (https://ffmpeg.org)."); process.exit(1); }
}
console.log(`✓ Node ${process.versions.node}, FFmpeg vorhanden`);

// 2) Node-Pakete (HyperFrames-CLI)
if (!fs.existsSync(path.join(ROOT, "node_modules", ".bin", "hyperframes"))) run("npm install --no-audit --no-fund");

// 3) Python-Pakete (Stimme, Aussprache, Audio)
const py = (mod) => { try { execSync(`python3 -c "import ${mod}"`, { stdio: "ignore" }); return true; } catch { return false; } };
const pip = "python3 -m pip install -q --disable-pip-version-check";
if (!py("scipy") || !py("piper") || !py("onnx")) run(`${pip} numpy scipy piper-tts==1.8.0 onnx`);
if (!py("torch") || !py("torchaudio") || !py("torchcodec")) run(`${pip} torch==2.15.0 torchaudio==2.11.1 torchcodec==0.17.0`);
if (!py("TTS") || !py("gruut_lang_de")) {
  run(`${pip} --use-pep517 coqui-tts==0.28.0 "gruut[de]==2.4.0"`);
}
// OmniVoice (Erzählerstimme, Engine aus VoiceStudio) + Whisper (Wortzeiten, Verständlichkeits-Check)
if (!py("omnivoice") || !py("faster_whisper") || !py("jiwer")) {
  run(`${pip} --no-deps omnivoice==0.2.1`);
  run(`${pip} pydub tensorboardX webdataset audioop-lts soundfile librosa "transformers>=5.3.0" accelerate faster-whisper jiwer rapidfuzz`);
}
console.log("✓ Python-Pakete");

// 4) Stimmen (kostenlos, von GitHub-Releases)
fs.mkdirSync(VOICES, { recursive: true });
const coqui = path.join(VOICES, "tts_models--de--thorsten--vits");
if (!fs.existsSync(path.join(coqui, "model_file.pth"))) {
  run(`curl -sSL -o thorsten-vits.zip https://github.com/coqui-ai/TTS/releases/download/v0.7.0_models/tts_models--de--thorsten--vits.zip && unzip -o -q thorsten-vits.zip && rm thorsten-vits.zip`, { cwd: VOICES });
}
if (!fs.existsSync(path.join(VOICES, "de-karlsson-low.onnx"))) {
  run(`curl -sSL https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-de-karlsson-low.tar.gz | tar xz`, { cwd: VOICES });
}
console.log("✓ Stimmen: Coqui Thorsten (Standard), Piper Karlsson (Reserve)");
// Bild-Schärfung (Real-ESRGAN x2, BSD-3) – kostenlos von GitHub
const MODELS = path.join(path.dirname(VOICES), "models");
fs.mkdirSync(MODELS, { recursive: true });
if (!fs.existsSync(path.join(MODELS, "RealESRGAN_x2plus.pth"))) {
  run(`curl -sSL -o RealESRGAN_x2plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth`, { cwd: MODELS });
}
if (!py("spandrel")) run(`${pip} spandrel`);
console.log("✓ Bild-Schärfung (Real-ESRGAN)");

// 5) Chrome für HyperFrames
try { run(`${path.join(ROOT, "node_modules", ".bin", "hyperframes")} browser ensure`); } catch { console.warn("⚠ hyperframes browser ensure fehlgeschlagen – Rendern prüft das erneut."); }
console.log("\nFertig. Nächster Schritt: npm run batch");
