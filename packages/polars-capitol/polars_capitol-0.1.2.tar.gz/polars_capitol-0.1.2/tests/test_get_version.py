import polars as pl
import polars_capitol as cap
import pytest


def test_version():
    df = pl.DataFrame(
        {
            "package_id": [
                "BILLS-118hr8070ih",
            ]
        }
    )
    s = pl.col("package_id").str.split(by="-").list.get(1, null_on_oob=True)
    expr = cap.version(s)
    result = df.with_columns(version=expr)

    expected_df = pl.DataFrame(
        {
            "package_id": [
                "BILLS-118hr8070ih",
            ],
            "version": [
                "ih",
            ],
        }
    )

    assert result.equals(expected_df)


def test_citation_without_version_raises():
    df = pl.DataFrame(
        {
            "package_id": [
                "BILLS-118hr8070",
            ]
        }
    )
    s = pl.col("package_id").str.split(by="-").list.get(1, null_on_oob=True)
    expr = cap.version(s)

    with pytest.raises(pl.exceptions.ComputeError) as exception:
        df.with_columns(version=expr)

    assert (
        str(exception.value)
        == "the plugin failed with message: `version` called on citation without version"
    )
