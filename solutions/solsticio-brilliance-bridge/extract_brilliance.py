#!/usr/bin/env python3
"""Solsticio Brilliance Bridge: deterministic brilliance extraction over a corpus.

Scores every document on eight faculties (awareness, intelligence, self-improving,
confidence, hope, style, joy, talent) from lexical and structural signals, derives
second-order compound faculties and a corpus-level brilliance field, extracts a
colour/structure genome from the showcase images, and QDP-seals the result
(SHA-256 + SHA-512 + SHA3-256 + SHA3-512 over canonical JSON).

The faculties are text-feature indices. They describe what a document talks about
and how it is built; they are not measurements of machine sentience.

Usage:
    python extract_brilliance.py [--external DIR ...] [--images DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SITE = HERE / "site"
ASSETS = SITE / "assets"
OUT = ASSETS / "brilliance.qdp.json"

FACULTIES = {
    "awareness": "aware observ monitor introspect self state detect health status sens attent conscious reflect doctor inspect probe notic watch".split(),
    "intelligence": "model infer reason llm agent predict learn neural token generat pipeline transformer quantiz cognit intellig think".split(),
    "self_improving": "improv optimi iterat recurs feedback refin evolv adapt retrain tune upgrad loop warmup benchmark grow compil".split(),
    "confidence": "verif proof prove assert check pass seal hash attest guarante determinist measur evidence gate test certain confiden".split(),
    "hope": "hope future vision mission goal next roadmap promis potential aspir wellbeing well-being opportun believ optim tomorrow".split(),
    "style": "style design font color colour palette gradient layout typograph aesthet elegan theme motion glow chrome visual".split(),
    "joy": "joy delight play fun celebrat happy bright wonder spark magic beaut smile game light dream".split(),
    "talent": "skill talent craft expert master capab abilit precis perform excel brilliant genius champion award fluen".split(),
}
COMPOUNDS = {
    "reflective_growth": ("awareness", "self_improving"),
    "credible_optimism": ("confidence", "hope"),
    "aesthetic_delight": ("style", "joy"),
    "applied_genius": ("intelligence", "talent"),
    "grounded_awareness": ("awareness", "confidence"),
    "playful_mastery": ("joy", "talent"),
    "visionary_reason": ("intelligence", "hope"),
    "stylish_evolution": ("style", "self_improving"),
}
STRUCTURAL = {
    "confidence": re.compile(
        r"\bassert\b|check\(|\bPASS\b|require\(|revert|sha3?_?\d{3}|keccak", re.I
    ),
    "awareness": re.compile(
        r"os\.path\.(isfile|exists)|/health|status|supportsInterface|doctor", re.I
    ),
    "self_improving": re.compile(r"\bfor\b .* in |\bwhile\b|recurs|retry", re.I),
    "intelligence": re.compile(
        r"from_pretrained|generate\(|pipeline\(|Llama\(|chat/completions", re.I
    ),
}
TOKEN = re.compile(r"[a-z][a-z\-]{2,}")


def qdp(data: bytes) -> dict[str, str]:
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
        "sha3_256": hashlib.sha3_256(data).hexdigest(),
        "sha3_512": hashlib.sha3_512(data).hexdigest(),
    }


def _js_numbers(obj):
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    if isinstance(obj, dict):
        return {k: _js_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_js_numbers(v) for v in obj]
    return obj


def canonical(obj) -> bytes:
    """Canonical JSON identical to the browser's canon(): sorted keys, no spaces, integral floats as ints."""
    return json.dumps(
        _js_numbers(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def read_text(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader

        return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    if suf == ".docx":
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf8", "ignore")
        return html.unescape(re.sub(r"<[^>]+>", " ", xml.replace("</w:p>", "\n")))
    raw = path.read_text("utf8", "ignore")
    if suf in {".html", ".htm"}:
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return raw


def faculty_counts(text: str) -> tuple[int, dict[str, int]]:
    tokens = TOKEN.findall(text.lower())
    counts = {}
    for fac, stems in FACULTIES.items():
        n = sum(1 for t in tokens if t.startswith(tuple(stems)))
        if fac in STRUCTURAL:
            n += len(STRUCTURAL[fac].findall(text))
        counts[fac] = n
    return len(tokens), counts


def entropy(vec: list[float]) -> float:
    s = sum(vec)
    if s <= 0:
        return 0.0
    ps = [v / s for v in vec if v > 0]
    return -sum(p * math.log(p) for p in ps) / math.log(len(vec))


def geomean(vec: list[float]) -> float:
    return math.exp(sum(math.log(max(v, 1.0)) for v in vec) / len(vec))


def cosine(a: list[float], b: list[float]) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def proof_run(log: Path) -> dict | None:
    if not log.is_file():
        return None
    checks = [
        {"id": m.group(2), "label": m.group(3).strip(), "pass": m.group(1) == "PASS"}
        for m in re.finditer(r"^(PASS|FAIL)\s+(T[\d.]+)\s+(.+)$", log.read_text(), re.M)
    ]
    return {
        "runner": "hermes-spine/proof/run_proof.mjs · EthereumJS VM · Node 22",
        "passed": sum(c["pass"] for c in checks),
        "total": len(checks),
        "checks": checks,
    }


def image_genome(path: Path) -> dict:
    from PIL import Image, ImageFilter, ImageStat

    img = Image.open(path).convert("RGB")
    small = img.copy()
    small.thumbnail((256, 256))
    pal = small.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    rgb = pal.getpalette()[:18]
    counts = sorted(pal.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    palette = [
        {
            "hex": "#%02x%02x%02x" % tuple(rgb[i * 3 : i * 3 + 3]),
            "share": round(c / total, 4),
        }
        for c, i in counts
    ]
    raw = small.tobytes()
    px = [tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)]
    rg = [r - g for r, g, b in px]
    yb = [(r + g) / 2 - b for r, g, b in px]

    def sd(xs):
        m = sum(xs) / len(xs)
        return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)), m

    (srg, mrg), (syb, myb) = sd(rg), sd(yb)
    colourfulness = math.sqrt(srg**2 + syb**2) + 0.3 * math.sqrt(mrg**2 + myb**2)
    grey = small.convert("L")
    edges = ImageStat.Stat(grey.filter(ImageFilter.FIND_EDGES)).mean[0] / 255
    flip = grey.transpose(Image.FLIP_LEFT_RIGHT)
    sym = 1 - sum(abs(a - b) for a, b in zip(grey.tobytes(), flip.tobytes())) / (
        255 * grey.width * grey.height
    )
    rich = small.quantize(colors=16, method=Image.Quantize.MEDIANCUT).getpalette()[:48]
    sat = []
    for i in range(16):
        r, g, b = rich[i * 3 : i * 3 + 3]
        mx, mn = max(r, g, b), min(r, g, b)
        sat.append(
            (((mx - mn) / mx if mx else 0) * (mx / 255), "#%02x%02x%02x" % (r, g, b))
        )
    accents = [h for _, h in sorted(sat, reverse=True)[:3]]
    return {
        "accents": accents,
        "width": img.width,
        "height": img.height,
        "luminance": round(ImageStat.Stat(grey).mean[0] / 255, 4),
        "colourfulness": round(colourfulness, 2),
        "edge_density": round(edges, 4),
        "symmetry": round(sym, 4),
        "palette": palette,
    }


def web_plate(src: Path, dst: Path, max_side: int) -> None:
    from PIL import Image

    img = Image.open(src).convert("RGB")
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    img.save(dst, "JPEG", quality=84, optimize=True, progressive=True)


IMAGES = [
    ("sol_girl2jpg.jpg", "sol-sovereign.jpg", "Sol · The Sovereign Gaze", 1600),
    ("eye_candiedc.png", "eye-candied.jpg", "Eye Candied · Gold-Cyan Iris", 1600),
    (
        "b3a85be7cfca994ac66458edaa10711b36bfbed3f049e76375cb724b7aaee2be.png",
        "chrome-lattice.jpg",
        "Chrome Lattice",
        1600,
    ),
    ("globuletoo.png", "globule.jpg", "Globule · Orbital Cell", 1600),
    (
        "OUR_POWER_Main_Brain_P32_8K_Poster.jpg",
        "main-brain-p32.jpg",
        "OUR POWER · Main Brain P32",
        2560,
    ),
]

PRIVATE_HINTS = (
    "sealed",
    "private",
    "overseer",
    "measured_result",
    "harness architecture",
    "investor",
)


def collect(external: list[Path]) -> list[tuple[str, str, Path, bool]]:
    docs = []
    for p in sorted((REPO / "utilities" / "model-card-tools").rglob("*_test.py")):
        docs.append(("repo-test", str(p.relative_to(REPO)), p, False))
    exts = {".py", ".ts", ".mjs", ".sol", ".md", ".html", ".pdf", ".docx", ".toml"}
    for root in external:
        for p in sorted(root.rglob("*")):
            if (
                not p.is_file()
                or p.suffix.lower() not in exts
                or "node_modules" in p.parts
                or "artifacts" in p.parts
            ):
                continue
            private = any(h in p.name.lower() for h in PRIVATE_HINTS)
            kind = {
                ".sol": "contract",
                ".mjs": "proof",
                ".pdf": "document",
                ".docx": "document",
            }.get(p.suffix.lower(), "source")
            docs.append((kind, f"{root.name}/{p.relative_to(root)}", p, private))
    return docs


def build(external: list[Path], images: Path | None) -> dict:
    rows = []
    for kind, label, path, private in collect(external):
        text = read_text(path)
        n, counts = faculty_counts(text)
        if n < 20:
            continue
        rows.append(
            {
                "id": hashlib.sha256(label.encode()).hexdigest()[:12],
                "label": "private document · fingerprint only" if private else label,
                "kind": kind,
                "private": private,
                "tokens": n,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "density": {f: round(c * 1000 / n, 3) for f, c in counts.items()},
            }
        )
    peak = {f: max(r["density"][f] for r in rows) or 1 for f in FACULTIES}
    for r in rows:
        r["faculties"] = {
            f: round(100 * r["density"][f] / peak[f], 2) for f in FACULTIES
        }
        vec = list(r["faculties"].values())
        r["brilliance"] = round(geomean(vec), 2)
        r["harmony"] = round(entropy(vec), 4)
    centroid = {
        f: round(sum(r["faculties"][f] for r in rows) / len(rows), 2) for f in FACULTIES
    }
    cvec = list(centroid.values())
    for r in rows:
        r["coherence"] = round(cosine(list(r["faculties"].values()), cvec), 4)
    compounds = {
        k: round(math.sqrt(centroid[a] * centroid[b]), 2)
        for k, (a, b) in COMPOUNDS.items()
    }
    rows.sort(key=lambda r: -r["brilliance"])
    body = {
        "title": "Solsticio Brilliance Bridge",
        "method": {
            "faculty": "density = hits per 1000 tokens (stem lexicon + structural code signals); score = 100 * density / corpus peak",
            "brilliance": "geometric mean of the eight faculty scores (floor 1) — rewards balance over spikes",
            "harmony": "normalised Shannon entropy of the faculty vector, 0..1",
            "coherence": "cosine similarity of a document vector to the corpus centroid",
            "compound": "sqrt(a * b) over centroid faculties — a second-order faculty is only high when both parents are",
            "caveat": "text-feature indices, not measurements of awareness, feeling or sentience",
        },
        "lexicon": FACULTIES,
        "compound_pairs": COMPOUNDS,
        "corpus": {
            "documents": len(rows),
            "tokens": sum(r["tokens"] for r in rows),
            "private_fingerprinted": sum(r["private"] for r in rows),
            "kinds": {
                k: sum(r["kind"] == k for r in rows)
                for k in sorted({r["kind"] for r in rows})
            },
        },
        "centroid": centroid,
        "corpus_brilliance": round(geomean(cvec), 2),
        "corpus_harmony": round(entropy(cvec), 4),
        "compounds": compounds,
        "documents": rows,
        "proof_run": next(
            (
                pr
                for root in external
                if (pr := proof_run(root / "hermes-spine" / "proof" / "run.log"))
            ),
            None,
        ),
        "runtime_genome": runtime_genome(),
        "plates": [],
    }
    if images:
        for src, dst, title, side in IMAGES:
            matches = list(images.rglob(src))
            if not matches:
                continue
            target = ASSETS / dst
            web_plate(matches[0], target, side)
            body["plates"].append(
                {
                    "file": dst,
                    "title": title,
                    "source": src,
                    "source_sha256": hashlib.sha256(
                        matches[0].read_bytes()
                    ).hexdigest(),
                    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                    "genome": image_genome(matches[0]),
                }
            )
    elif OUT.is_file():
        body["plates"] = json.loads(OUT.read_text())["plates"]
    return body


def runtime_genome() -> list[dict]:
    out = []
    for p in sorted((REPO / "utilities" / "model-card-tools").rglob("*_test.py")):
        src = p.read_text()
        out.append(
            {
                "file": str(p.relative_to(REPO)),
                "engine": (
                    "llama.cpp GGUF"
                    if "llama_cpp" in src
                    else (
                        "Optimum-Intel IPEX"
                        if "IPEX" in src
                        else "Intel Extension for Transformers"
                    )
                ),
                "default_model": (
                    re.search(r"default=['\"]([^'\"]*(?:/|gguf)[^'\"]*)['\"]", src)
                    or re.search(r"['\"](Intel/[^'\"]+)['\"]", src)
                    or [None, None]
                )[1],
                "quantisation": (
                    "GGUF Q4"
                    if "gguf" in src.lower()
                    else (
                        "4-bit (load_in_4bit)"
                        if "load_in_4bit" in src
                        else "bf16/fp32 IPEX"
                    )
                ),
                "prompt": (
                    re.search(r"default=['\"](Can you[^'\"]*)['\"]", src)
                    or [None, None]
                )[1],
                "lines": src.count("\n") + 1,
            }
        )
    return out


def seal(body: dict) -> dict:
    body = {k: v for k, v in body.items() if k != "qdp_seal"}
    body = _js_numbers(body)
    body["qdp_seal"] = qdp(canonical(body))
    return body


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--external",
        type=Path,
        action="append",
        default=[],
        help="extra corpus root (repeatable)",
    )
    ap.add_argument(
        "--images", type=Path, help="folder containing the showcase source images"
    )
    a = ap.parse_args()
    ASSETS.mkdir(parents=True, exist_ok=True)
    body = seal(build(a.external, a.images))
    OUT.write_text(json.dumps(body, indent=1, ensure_ascii=False) + "\n")
    c = body["corpus"]
    print(
        f"{c['documents']} docs · {c['tokens']} tokens · brilliance {body['corpus_brilliance']} · seal {body['qdp_seal']['sha256'][:16]} -> {OUT}"
    )


if __name__ == "__main__":
    main()
