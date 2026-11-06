import json
import unittest

import extract_brilliance as eb


class TestBrilliance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(eb.OUT.read_text())

    def test_qdp_seal_matches_canonical_body(self):
        body = {k: v for k, v in self.manifest.items() if k != "qdp_seal"}
        self.assertEqual(eb.qdp(eb.canonical(body)), self.manifest["qdp_seal"])

    def test_plate_files_match_recorded_sha256(self):
        import hashlib

        for p in self.manifest["plates"]:
            data = (eb.ASSETS / p["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), p["sha256"], p["file"])

    def test_scores_bounded_and_sorted(self):
        docs = self.manifest["documents"]
        for d in docs:
            self.assertEqual(set(d["faculties"]), set(eb.FACULTIES))
            self.assertTrue(all(0 <= v <= 100 for v in d["faculties"].values()))
            self.assertTrue(0 <= d["harmony"] <= 1)
        self.assertEqual(
            [d["brilliance"] for d in docs],
            sorted((d["brilliance"] for d in docs), reverse=True),
        )

    def test_private_documents_are_fingerprint_only(self):
        for d in self.manifest["documents"]:
            if d["private"]:
                self.assertEqual(d["label"], "private document · fingerprint only")

    def test_repo_tests_are_in_corpus(self):
        labels = {
            d["label"] for d in self.manifest["documents"] if d["kind"] == "repo-test"
        }
        self.assertEqual(len(labels), 3)
        self.assertEqual(len(eb.runtime_genome()), 3)

    def test_math_primitives(self):
        self.assertAlmostEqual(eb.entropy([1] * 8), 1.0)
        self.assertEqual(eb.entropy([0] * 8), 0.0)
        self.assertAlmostEqual(eb.geomean([4, 4, 4, 4, 4, 4, 4, 4]), 4.0)
        self.assertAlmostEqual(eb.cosine([1, 0], [2, 0]), 1.0)

    def test_extraction_is_deterministic(self):
        text = "We verify, measure and seal. assert ok. The model will infer with hope and joy."
        self.assertEqual(eb.faculty_counts(text), eb.faculty_counts(text))
        n, c = eb.faculty_counts(text)
        self.assertGreater(c["confidence"], 0)
        self.assertGreater(c["hope"], 0)


if __name__ == "__main__":
    unittest.main()
