# Solsticio · Brilliance Bridge

A single-page dashboard that reads a corpus (the three Intel inference tests in this repo plus any extra folders you point it at) and scores every document on eight **faculties**: awareness, intelligence, self-improving, confidence, hope, style, joy and talent. It then builds higher-order views on top of those scores:

| Level | What it is | Maths |
|---|---|---|
| I · Octave | 8-faculty radar per document and for the corpus centroid | density = hits / 1000 tokens (stem lexicon + structural code signals), normalised to corpus peak |
| II · Compounds | 8 paired faculties (e.g. credible optimism = confidence × hope) | `sqrt(a * b)`, so a compound is only high when both faculties are |
| III · Field | Documents projected into 2-D brilliance space | PCA via power iteration (in-browser) + summed Gaussian potentials, drawn as iso-contours |
| Ascension Lab | Re-weight the octave to re-rank the corpus and drive a generative flow field | weighted geometric mean; seeded flow field; QDP receipt per composition |

It also shows the Hermes Spine proof run exactly as observed (including failures), the runtime genome of the three `*_test.py` files, and a style genome for each showcase image (median-cut palette, Hasler–Süsstrunk colourfulness, edge density, mirror symmetry).

`site/assets/brilliance.qdp.json` is sealed with **SHA-256 + SHA-512 + SHA3-256 + SHA3-512** over canonical JSON. The page re-computes all four in the browser (the Keccak sponge is inline and self-tests against FIPS 202 vectors) and re-hashes every image plate.

> The faculties are text-feature indices: they describe what documents talk about and how they are built. They do not measure awareness, feeling or sentience in any model.

## Run

```bash
cd solutions/solsticio-brilliance-bridge/site
python3 -m http.server 8000   # file:// blocks fetch + Web Crypto
```

## Regenerate

```bash
pip install pillow pypdf
python3 extract_brilliance.py --external /path/to/extra/corpus --images /path/to/images
python3 -m unittest test_extract_brilliance
```

If `--images` is omitted, existing plates are kept. Filenames matching `sealed`, `private`, `overseer`, `measured_result`, `harness architecture` or `investor` are included as **fingerprint only**: the manifest keeps their SHA-256 and faculty vector, but not their name or any text.
