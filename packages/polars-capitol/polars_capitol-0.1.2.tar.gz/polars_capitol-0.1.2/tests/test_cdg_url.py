import polars as pl
import polars_capitol as cap


def test_cdg_url():
    df = pl.DataFrame(
        {
            "package_id": [
                "BILLS-118hr8070",
                "BILLS-118hr8070ih",
                "BILLS-118s25",
                "CRPT-118hrpt529",
                "CPRT-119hprt58246",
            ]
        }
    )
    s = pl.col("package_id").str.split(by="-").list.get(1, null_on_oob=True)
    expr = cap.cdg_url(s)
    result = df.with_columns(cdg_url=expr)

    expected_df = pl.DataFrame(
        {
            "package_id": [
                "BILLS-118hr8070",
                "BILLS-118hr8070ih",
                "BILLS-118s25",
                "CRPT-118hrpt529",
                "CPRT-119hprt58246",
            ],
            "cdg_url": [
                "https://www.congress.gov/bill/118th-congress/house-bill/8070",
                "https://www.congress.gov/bill/118th-congress/house-bill/8070/text/ih",
                "https://www.congress.gov/bill/118th-congress/senate-bill/25",
                "https://www.congress.gov/congressional-report/118th-congress/house-report/529",
                "https://www.congress.gov/committee-print/119th-congress/house-committee-print/58246",
            ],
        }
    )

    assert result.equals(expected_df)
