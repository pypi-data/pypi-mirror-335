"""命令行生成器"""

if __name__ == "__main__":
    import polars as pl

    df = pl.read_database_uri("select * from test", "sqlite://test.db")
    # conn = sqlite3.connect("test.db")
    df.write_database(
        "test2", "sqlite://test.db", if_table_exists="replace", engine="adbc"
    )
    print(pl.read_database_uri("select * from test2", "sqlite://test.db"))
