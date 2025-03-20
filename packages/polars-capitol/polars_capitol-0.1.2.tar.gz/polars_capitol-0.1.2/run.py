import polars as pl
import polars_capitol as cap


df = pl.DataFrame(
    {
        "package_id": [
            "BILLS-118hr8070",
            "BILLS-118hr8070ih",
            "BILLS-118s25",
            "CRPT-118hrpt529",
        ]
    }
)
s = pl.col("package_id").str.split(by="-").list.get(1, null_on_oob=True)
expr = cap.cdg_url(s)
result = df.with_columns(cdg_url=expr)
expr = cap.version(s)
result = df.with_columns(version=expr)

print(result)
