from pathlib import Path

from cms_claims.transform import clean_claims
from cms_claims.demo_data import make_demo


def test_clean_claims(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    clean = tmp_path / "clean.csv"
    make_demo(500, 7).to_csv(raw, index=False)
    report = clean_claims(raw, clean, high_cost_quantile=0.9)
    assert clean.exists()
    assert report["after"]["rows"] == 500
    assert report["high_cost_threshold"] > 0
