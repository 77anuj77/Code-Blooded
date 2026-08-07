"""Download the Orphanet XML products used by ingest.orphadata.

Orphadata publishes these under CC-BY 4.0 at a stable path, so no account or
manual download is needed despite what older docs claimed.

Files are saved into the nested layout packages/ingest/orphadata.py expects.
"""

import argparse
import sys
from pathlib import Path
from urllib.request import urlretrieve

ORPHADATA_BASE = "https://www.orphadata.com/data/xml"

# filename -> path relative to the orphadata root, matching the PRODUCT*
# constants in packages/ingest/orphadata.py exactly.
PRODUCTS = {
    "en_product1.xml": Path("Rare diseases and classifications")
    / "Cross-referencing of rare diseases"
    / "XML",
    "en_product4.xml": Path("Rare diseases with associated phenotypes"),
    "en_product6.xml": Path("Genes associated with rare diseases"),
    "en_product9_prev.xml": Path("Epidemiological data") / "Rare disease epidemiology",
}


def download_file(url: str, dest: Path, description: str) -> bool:
    print(f"Downloading {description} from {url} ...")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(url, dest)

        # A stray HTML error page would still be written, so check it parses as XML.
        with open(dest, "rb") as f:
            head = f.read(64).lstrip()
        if not head.startswith(b"<?xml"):
            print(f"  ERROR: {dest.name} is not XML (got {head[:32]!r})")
            return False

        print(f"  Saved to {dest} ({dest.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  ERROR: Failed to download {description}: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Orphanet XML products")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "orphadata",
        help="Directory to save the XML products (default: data/orphadata/)",
    )
    args = parser.parse_args()

    ok = True
    for filename, subdir in PRODUCTS.items():
        dest = args.data_dir / subdir / filename
        if not download_file(f"{ORPHADATA_BASE}/{filename}", dest, filename):
            ok = False

    if ok:
        print("\nAll Orphadata products downloaded successfully!")
        print(f"Files saved under: {args.data_dir}")
        return 0

    print("\nSome downloads failed. Check errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
