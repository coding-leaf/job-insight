"""Database seeding script for JobInsight.

Reads data/processed/jobs_cleaned_grouped.json and imports into MongoDB collection 'jobs',
creating 4 required indexes and validating document count (2,251).
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_DB_NAME = "job_insight"
DEFAULT_COLL_NAME = "jobs"
EXPECTED_DOC_COUNT = 2251

# The 4 required indexes
REQUIRED_INDEXES = [
    (
        [("job_category", pymongo.ASCENDING), ("province", pymongo.ASCENDING)],
        "idx_category_province",
    ),
    (
        [
            ("salary_eligible_for_midpoint", pymongo.ASCENDING),
            ("job_category", pymongo.ASCENDING),
        ],
        "idx_salary_category",
    ),
    ([("education_min_code", pymongo.ASCENDING)], "idx_education_min_code"),
    ([("skills.skill_name", pymongo.ASCENDING)], "idx_skills_name"),
]


def resolve_data_file(custom_path: str | None = None) -> Path:
    """Resolve path to jobs_cleaned_grouped.json."""
    if custom_path:
        p = Path(custom_path)
        if p.is_file():
            return p

    candidates = [
        Path(__file__).resolve().parents[3] / "data" / "processed" / "jobs_cleaned_grouped.json",
        Path(__file__).resolve().parents[2] / "data" / "processed" / "jobs_cleaned_grouped.json",
        Path("data/processed/jobs_cleaned_grouped.json").resolve(),
    ]
    for c in candidates:
        if c.is_file():
            return c
    raise FileNotFoundError("Could not locate data/processed/jobs_cleaned_grouped.json")


def load_jobs_data(data_path: Path) -> list[dict[str, Any]]:
    """Load JSON jobs data from file."""
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise TypeError(f"Expected list of jobs in JSON, got {type(data)}")
    return data


def seed_mongodb(
    mongodb_url: str = "mongodb://localhost:27017",
    db_name: str = DEFAULT_DB_NAME,
    coll_name: str = DEFAULT_COLL_NAME,
    data_path: str | None = None,
    dry_run: bool = False,
) -> bool:
    """Seed MongoDB with cleaned and grouped jobs data and create indexes."""
    target_file = resolve_data_file(data_path)
    logger.info("Loading dataset from %s", target_file)
    jobs = load_jobs_data(target_file)
    total_loaded = len(jobs)
    logger.info("Loaded %d documents from file.", total_loaded)

    if total_loaded != EXPECTED_DOC_COUNT:
        logger.error(
            "Document count mismatch! Expected %d, got %d",
            EXPECTED_DOC_COUNT,
            total_loaded,
        )
        return False

    if dry_run:
        logger.info("[DRY RUN] Verified JSON data containing %d records.", total_loaded)
        return True

    logger.info("Connecting to MongoDB at %s ...", mongodb_url)
    try:
        client: MongoClient = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[db_name]
        coll = db[coll_name]

        # Reset collection
        logger.info("Clearing existing collection '%s' in database '%s'...", coll_name, db_name)
        coll.delete_many({})

        # Insert records
        logger.info("Inserting %d documents...", total_loaded)
        result = coll.insert_many(jobs)
        inserted_count = len(result.inserted_ids)
        logger.info("Successfully inserted %d documents.", inserted_count)

        if inserted_count != EXPECTED_DOC_COUNT:
            raise RuntimeError(f"Inserted count {inserted_count} != expected {EXPECTED_DOC_COUNT}")

        # Create indexes
        logger.info("Creating required indexes...")
        for keys, name in REQUIRED_INDEXES:
            idx_name = coll.create_index(keys, name=name)
            logger.info("Created index '%s' with keys %s", idx_name, keys)

        # Validate count and indexes
        actual_count = coll.count_documents({})
        index_info = coll.index_information()
        logger.info("Validation: Total documents in collection = %d", actual_count)
        logger.info("Validation: Current indexes = %s", list(index_info.keys()))

        if actual_count != EXPECTED_DOC_COUNT:
            logger.error("Validation failed: collection count is %d", actual_count)
            return False

        logger.info("Seeding completed successfully.")
        return True

    except (PyMongoError, OSError) as exc:
        logger.error("Failed to seed MongoDB: %s", exc)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed MongoDB with JobInsight dataset")
    parser.add_argument(
        "--mongodb-url",
        default="mongodb://localhost:27017",
        help="MongoDB connection URL",
    )
    parser.add_argument(
        "--db-name",
        default=DEFAULT_DB_NAME,
        help="Target database name",
    )
    parser.add_argument(
        "--data-path",
        default=None,
        help="Path to jobs_cleaned_grouped.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate dataset without writing to MongoDB",
    )

    args = parser.parse_args()
    success = seed_mongodb(
        mongodb_url=args.mongodb_url,
        db_name=args.db_name,
        data_path=args.data_path,
        dry_run=args.dry_run,
    )
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
