"""Download ClinVar gene-disease mapping file.

Downloads the gene_condition_source_id TSV file from NCBI ClinVar FTP.

File is saved to data/clinvar/gene_condition_source_id
"""

import argparse
import gzip
import sys
from pathlib import Path
from urllib.request import urlretrieve


CLINVAR_FTP_BASE = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited"
CLINVAR_GENE_CONDITION_URL = f"{CLINVAR_FTP_BASE}/gene_condition_source_id"


def download_file(url: str, dest: Path, description: str) -> bool:
    """Download a file with progress indication."""
    print(f"Downloading {description} from {url} ...")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        # ClinVar file is gzipped
        gz_dest = dest.with_suffix(dest.suffix + ".gz")
        urlretrieve(url, gz_dest)
        print(f"  Downloaded to {gz_dest} ({gz_dest.stat().st_size:,} bytes)")

        # Decompress
        print(f"  Decompressing to {dest} ...")
        with gzip.open(gz_dest, "rb") as f_in:
            with open(dest, "wb") as f_out:
                f_out.write(f_in.read())
        gz_dest.unlink()  # Remove gzipped file
        print(f"  Saved to {dest} ({dest.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  ERROR: Failed to download {description}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download ClinVar gene-disease mapping")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "clinvar",
        help="Directory to save ClinVar file (default: data/clinvar/)",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    dest = data_dir / "gene_condition_source_id"
    success = download_file(CLINVAR_GENE_CONDITION_URL, dest, "ClinVar gene-condition-source-id")

    if success:
        print("\nClinVar file downloaded successfully!")
        print(f"File saved to: {dest}")
        return 0
    else:
        print("\nDownload failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())