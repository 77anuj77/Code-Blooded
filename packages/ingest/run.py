"""Run all ingest scripts in dependency order."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from ingest import clinvar, fgdd, hpo, orphadata  # noqa: E402
from ingest.db import init_db  # noqa: E402


def main():
    print("Initialising database schema...")
    init_db()
    print()

    orphadata.run()
    print()

    hpo.run()
    print()

    clinvar.run()
    print()

    fgdd.run()
    print()

    print("All ingest complete. Database written to Supabase (DATABASE_URL).")


if __name__ == "__main__":
    main()
