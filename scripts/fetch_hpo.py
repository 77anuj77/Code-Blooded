"""Download HPO ontology and annotation files.

Downloads:
- hp.obo: HPO ontology (OBO format)
- phenotype.hpoa: HPO phenotype annotations (disease-HPO associations)
- genes_to_phenotype.txt: Gene-to-phenotype mappings
- phenotype_to_genes.txt: Phenotype-to-gene mappings (transitive)

Files are saved to data/hpo/
"""

import argparse
import sys
from pathlib import Path
from urllib.request import urlretrieve


HPO_BASE_URL = "https://purl.obolibrary.org/obo/hp"
HPO_OBO_URL = f"{HPO_BASE_URL}.obo"

# 'latest' rather than a pinned tag: the previously hardcoded v2024-03-01 release
# was removed upstream and every one of these 404'd.
HPO_RELEASE_BASE = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download"
HPO_HPOA_URL = f"{HPO_RELEASE_BASE}/phenotype.hpoa"
HPO_GENES_URL = f"{HPO_RELEASE_BASE}/genes_to_phenotype.txt"
HPO_GENES_TRANSITIVE_URL = f"{HPO_RELEASE_BASE}/phenotype_to_genes.txt"


def download_file(url: str, dest: Path, description: str) -> bool:
    """Download a file with progress indication."""
    print(f"Downloading {description} from {url} ...")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(url, dest)
        print(f"  Saved to {dest} ({dest.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  ERROR: Failed to download {description}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download HPO data files")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "hpo",
        help="Directory to save HPO files (default: data/hpo/)",
    )
    parser.add_argument(
        "--skip-obo", action="store_true", help="Skip downloading hp.obo"
    )
    parser.add_argument(
        "--skip-hpoa", action="store_true", help="Skip downloading phenotype.hpoa"
    )
    parser.add_argument(
        "--skip-genes", action="store_true", help="Skip downloading gene mappings"
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    results = []

    if not args.skip_obo:
        results.append(
            download_file(
                HPO_OBO_URL, data_dir / "hp.obo", "HPO ontology (hp.obo)"
            )
        )

    if not args.skip_hpoa:
        results.append(
            download_file(
                HPO_HPOA_URL, data_dir / "phenotype.hpoa", "HPO phenotype annotations (phenotype.hpoa)"
            )
        )

    if not args.skip_genes:
        results.append(
            download_file(
                HPO_GENES_URL, data_dir / "genes_to_phenotype.txt", "Gene-to-phenotype mappings (genes_to_phenotype.txt)"
            )
        )
        results.append(
            download_file(
                HPO_GENES_TRANSITIVE_URL, data_dir / "phenotype_to_genes.txt", "Phenotype-to-gene mappings (phenotype_to_genes.txt)"
            )
        )

    if all(results):
        print("\nAll HPO files downloaded successfully!")
        print(f"Files saved to: {data_dir}")
        return 0
    else:
        print("\nSome downloads failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())