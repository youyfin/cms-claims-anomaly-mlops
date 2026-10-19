from pathlib import Path

from cms_claims.demo_data import make_demo
from cms_claims.sql_features import build_provider_features
from cms_claims.transform import clean_claims


def test_provider_features(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    clean = tmp_path / "clean.csv"
    db = tmp_path / "claims.db"
    out = tmp_path / "provider.csv"
    sql = Path(__file__).resolve().parents[1] / "sql" / "provider_features.sql"
    make_demo(800, 11).to_csv(raw, index=False)
    clean_claims(raw, clean)
    features = build_provider_features(clean, db, sql, out)
    assert not features.empty
    assert "claims_per_beneficiary" in features.columns
    assert features["claim_count"].sum() == 800
