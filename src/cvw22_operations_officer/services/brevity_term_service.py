# Copyright 2026 Niklas Glienke

import logging
import sqlite3
from pathlib import Path

from cvw22_operations_officer.models.brevity_term_model import BrevityTerm


class BrevityTermService:
    """Provide interaction with the stored brevity terms."""

    def __init__(self, db_path: Path):
        """Initialize the database.

        Args:
            db_path: Path to the sqlite database file.

        """
        self.DB_PATH = db_path
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")

    def _reset_used_in_digest(self) -> None:
        """Reset used_in_digest attribute for all brevity terms."""
        self.logger.info(
            "Reset 'used_in_digest' to '0' for all brevity terms."
        )

        with sqlite3.connect(self.DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE brevity_term SET used_in_digest = 0")
            connection.commit()

    def _set_used_in_digest(self, term: str) -> None:
        """Set used_in_digest attribute of a brevity term to used.

        Args:
            term: Term of the desired brevity term to set used_in_digest
              attribute.

        """
        self.logger.info(f"Set 'used_in_digest' to '1' for {term}")

        with sqlite3.connect(self.DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE brevity_term SET used_in_digest = 1 WHERE term = ?",
                (term,),
            )
            connection.commit()

    def get_brevity_terms_by_term(
        self, term: str, limit: int = 5
    ) -> list[BrevityTerm]:
        """Get all matching brevity terms from the given term.

        Args:
            term: The term to search for.
            limit: The limit of returned brevity terms.

        Returns:
            A list of maximum 5 matching brevity terms. If no brevity term
            matches, the list is going to be empty. Each brevity term in the
            list is a BrevityTerm object.

        """
        matching_brevity_terms: list[BrevityTerm] = []

        self.logger.info(
            f"Search for brevity terms with '{term}' in the database."
        )

        with sqlite3.connect(self.DB_PATH) as connection:
            cursor = connection.cursor()
            response = cursor.execute(
                "SELECT term, description FROM brevity_term WHERE term LIKE ?",
                (f"%{term}%",),
            )
            fetched_brevity_terms = response.fetchmany(limit)

        if not fetched_brevity_terms:
            self.logger.info("No matching brevity term found in the database.")
            return []

        for term, description in fetched_brevity_terms:
            matching_brevity_terms.append(BrevityTerm(term, description))

        return matching_brevity_terms

    def get_brevity_term_for_digest(self) -> BrevityTerm:
        """Get a yet unused brevity term for the digest.

        Returns:
            A unused brevity term as a BrevityTerm object for the digest.

        """
        self.logger.info(
            "Get a yet unused brevity term for the digest from the database."
        )

        while True:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                response = cursor.execute(
                    "SELECT term, description FROM brevity_term "
                    "WHERE used_in_digest = 0 "
                    "LIMIT 1"
                )
                brevity_term_for_digest = response.fetchone()

            if brevity_term_for_digest is None:
                self.logger.info("No unused brevity term found.")
                self._reset_used_in_digest()
                continue

            self.logger.info("Unused brevity term found.")
            self._set_used_in_digest(brevity_term_for_digest[0])

            return BrevityTerm(*brevity_term_for_digest)
