from setuptools import find_packages, setup

entry_point = "anysqldiag = anysqldiag.__main__:main"


with open("requirements.txt", encoding="utf-8") as f:
    requires = []
    for line in f:
        req = line.split("#", 1)[0].strip()
        if req and not req.startswith("--"):
            requires.append(req)

long_description = """
Please see:
https://github.com/Minyus/any-sql-diag
"""

DIALECTS = [
    "Athena",
    "BigQuery",
    "ClickHouse",
    "Databricks",
    "Doris",
    "Drill",
    "Druid",
    "DuckDB",
    "Dune",
    "Hive",
    "Materialize",
    "MySQL",
    "Oracle",
    "Postgres",
    "Presto",
    "PRQL",
    "Redshift",
    "RisingWave",
    "Snowflake",
    "Spark",
    "Spark2",
    "SQLite",
    "StarRocks",
    "Tableau",
    "Teradata",
    "Trino",
    "TSQL",
]

setup(
    name="anysqldiag",
    version="0.0.3",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": [entry_point]},
    install_requires=requires,
    description="CLI to diagnose any SQL using sqlglot",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Minyus/any-sql-diag",
    author="Yusuke Minami",
    author_email="me@minyus.github.com",
    zip_safe=False,
    keywords=", ".join(["SQL", "sqlglot"] + DIALECTS),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
)
