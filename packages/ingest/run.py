"""Run all ingest scripts in dependency order."""

from ingest import clinvar, fgdd, hpo, orphadata
from ingest.db import init_db  # importing this loads the root .env


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
