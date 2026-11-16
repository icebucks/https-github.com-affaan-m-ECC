// Stimme erzeugen: ElevenLabs (wenn ELEVENLABS_API_KEY gesetzt) oder lokal mit Piper.
// Ergebnis: voice.wav + words.json ({duration, words:[{text,start,end,satz}]}).
// Wird gecacht: gleicher Text + gleiche Stimme = keine neue Erzeugung (spart Zeichen).
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { splitSentences } from "./compose.mjs";

export const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
// Stimmen liegen außerhalb des Repos (vom Setup bzw. Umgebungs-Setup-Skript befüllt)
export const VOICE_DIR = process.env.VOICE_DIR || path.join(process.env.HOME || ROOT, ".cache", "ich-war-dabei", "voices");
const PIPER_VOICE = process.env.PIPER_VOICE || "de-karlsson-low";
const COQUI_DIR = path.join(VOICE_DIR, "tts_models--de--thorsten--vits");
// Standard: Coqui „Thorsten“ (22 kHz, deutlich sauberer). TTS_ENGINE=piper erzwingt die alte Stimme.
const hasOmni = (() => { try { execFileSync("python3", ["-c", "import omnivoice, faster_whisper"], { stdio: "ignore" }); return true; } catch { return false; } })();
// Standard: OmniVoice (VoiceStudio-Engine, beste Verständlichkeit im Test: 0 % Wortfehler).
// Reserve: Coqui Thorsten, dann Piper. Erzwingen mit TTS_ENGINE=omni|coqui|piper.
const LOCAL = process.env.TTS_ENGINE || (hasOmni ? "omni" : fs.existsSync(COQUI_DIR) ? "coqui" : "piper");

export async function makeVoice(script, outDir) {
  const sentences = splitSentences(script.erzaehltext);
  const useEleven = Boolean(process.env.ELEVENLABS_API_KEY);
  const lexHash = crypto.createHash("sha1").update(fs.readFileSync(path.join(ROOT, "pipeline", "aussprache.json"))).digest("hex").slice(0, 8);
  const engine = useEleven ? `elevenlabs:${process.env.ELEVENLABS_VOICE_ID || "default"}` : LOCAL === "omni" ? "omni:erzaehler-v2-B-schnell" : LOCAL === "coqui" ? `coqui:thorsten-vits:lex${lexHash}` : `piper:${PIPER_VOICE}`;
  const hash = crypto.createHash("sha1").update(engine + "\n" + sentences.join("\n")).digest("hex").slice(0, 12);
  const wav = path.join(outDir, "voice.wav");
  const wordsFile = path.join(outDir, "words.json");
  const stamp = path.join(outDir, "voice.hash");
  if (fs.existsSync(wav) && fs.existsSync(wordsFile) && fs.existsSync(stamp) && fs.readFileSync(stamp, "utf8") === hash) {
    console.log(`  Stimme aus Cache (${engine})`);
    return JSON.parse(fs.readFileSync(wordsFile, "utf8"));
  }
  console.log(`  Stimme erzeugen mit ${engine} …`);
  if (useEleven) await elevenLabs(sentences, wav, wordsFile);
  else if (LOCAL === "omni") omni(sentences, wav, wordsFile);
  else if (LOCAL === "coqui") coqui(sentences, wav, wordsFile);
  else piper(sentences, wav, wordsFile);
  fs.writeFileSync(stamp, hash);
  const data = JSON.parse(fs.readFileSync(wordsFile, "utf8"));
  fs.writeFileSync(path.join(outDir, "transcript.txt"),
    data.words.map((w) => `${w.start.toFixed(2)}\t${w.end.toFixed(2)}\t${w.text}`).join("\n") + "\n");
  return data;
}

function omni(sentences, wav, wordsFile) {
  const req = path.join(path.dirname(wav), "tts_request.json");
  fs.writeFileSync(req, JSON.stringify({ sentences, out_wav: wav, out_words: wordsFile, speed: 1.0, num_step: 32, lead_in: 0.15 }, null, 1));
  execFileSync("python3", [path.join(ROOT, "pipeline", "tts_omni.py"), req], { stdio: ["ignore", "ignore", "inherit"] });
  fs.rmSync(req);
}

function coqui(sentences, wav, wordsFile) {
  const req = path.join(path.dirname(wav), "tts_request.json");
  fs.writeFileSync(req, JSON.stringify({ sentences, model_dir: COQUI_DIR, out_wav: wav, out_words: wordsFile, length_scale: 1.04, pitch: 0.91 }, null, 1));
  execFileSync("python3", [path.join(ROOT, "pipeline", "tts_coqui.py"), req], { stdio: ["ignore", "ignore", "inherit"] });
  fs.rmSync(req);
}

function piper(sentences, wav, wordsFile) {
  const model = path.join(VOICE_DIR, `${PIPER_VOICE}.onnx`);
  if (!fs.existsSync(model)) throw new Error(`Piper-Stimme fehlt: ${model}. Erst "npm run setup" ausführen.`);
  const req = path.join(path.dirname(wav), "tts_request.json");
  fs.writeFileSync(req, JSON.stringify({ sentences, voice: model, out_wav: wav, out_words: wordsFile, length_scale: 1.06 }, null, 1));
  execFileSync("python3", [path.join(ROOT, "pipeline", "tts_piper.py"), req], { stdio: ["ignore", "inherit", "pipe"] });
  fs.rmSync(req);
}

// ElevenLabs mit Zeichen-Zeitstempeln (ein einziger Take für den ganzen Text)
async function elevenLabs(sentences, wav, wordsFile) {
  const voiceId = process.env.ELEVENLABS_VOICE_ID || "onwK4e9ZLuTAKqWW03F9"; // tiefe, ruhige Erzählstimme
  const text = sentences.join(" ");
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/with-timestamps?output_format=mp3_44100_128`, {
    method: "POST",
    headers: { "xi-api-key": process.env.ELEVENLABS_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      model_id: process.env.ELEVENLABS_MODEL || "eleven_multilingual_v2",
      language_code: "de",
      voice_settings: { stability: 0.6, similarity_boost: 0.75, style: 0.15, use_speaker_boost: true, speed: 0.95 },
    }),
  });
  if (!res.ok) throw new Error(`ElevenLabs ${res.status}: ${await res.text()}`);
  const data = await res.json();
  const mp3 = wav.replace(/\.wav$/, ".mp3");
  fs.writeFileSync(mp3, Buffer.from(data.audio_base64, "base64"));
  // 0,5 s Vorlauf für den Hook, dann WAV
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", mp3, "-af", "adelay=500:all=1,apad=pad_dur=0.3", "-ar", "44100", "-ac", "1", wav]);
  const al = data.alignment;
  const words = [];
  let cur = null;
  // Satzgrenzen im Gesamttext (Zeichenposition)
  const bounds = [];
  let pos = 0;
  for (const s of sentences) { bounds.push(pos); pos += s.length + 1; }
  const satzAt = (i) => bounds.filter((b) => b <= i).length - 1;
  al.characters.forEach((ch, i) => {
    const isWordChar = /[\p{L}\p{N}]/u.test(ch);
    if (isWordChar) {
      if (!cur) cur = { text: "", start: al.character_start_times_seconds[i] + 0.5, satz: satzAt(i) };
      cur.text += ch;
      cur.end = al.character_end_times_seconds[i] + 0.5;
    } else if (/\s/.test(ch) || i === al.characters.length - 1) {
      if (cur) { words.push(cur); cur = null; }
    } else if (cur && /[-'’]/.test(ch)) {
      cur.text += ch;
    }
  });
  if (cur) words.push(cur);
  const dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).toString());
  words.forEach((w) => { w.start = Math.round(w.start * 1000) / 1000; w.end = Math.round(w.end * 1000) / 1000; });
  fs.writeFileSync(wordsFile, JSON.stringify({ duration: dur, words, warnings: [] }, null, 1));
}
