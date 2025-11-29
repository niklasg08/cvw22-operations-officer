# Copyright 2025 Niklas Glienke

import logging
import sqlite3
from pathlib import Path


class Database:
    """A database class to interact with the database.

    The database class takes the role of providing a connection between the bot
    and the database. Please note that the class only provides read operations
    for external code. However, it will change some parts of the database
    throughout the operation of the bot.
    """

    def __init__(self, config_dir: str | Path):
        """Initialize the database.

        Args:
            config_dir (str | Path): Path to the configuration directory.

        """
        self.CONFIG_DIR = Path(config_dir)
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")

        self.connection = sqlite3.connect(
            self.CONFIG_DIR / "cvw22_operations_officer.db"
        )
        self.cursor = self.connection.cursor()

    def get_brevity_term_by_name(self, name: str) -> list:
        """Get all matching brevity terms with a name.

        Args:
            name (str): The name to search for.

        Returns:
            list: A list of all matching brevity terms.

        """
        self.logger.info(
            f"Search for brevity term with '{name}' in the database."
        )
        response = self.cursor.execute(
            f"SELECT term, description FROM brevity_term WHERE term LIKE '%{name}%'"
        )
        brevity_terms = response.fetchmany(5)

        if brevity_terms is None:
            self.logger.info("No matching brevity term found in the database.")
            return []

        return brevity_terms

    def get_brevity_terms_for_digest(self) -> tuple:
        """Get a yet unused brevity term for the digest.

        Returns:
            tuple: A unused brevity term for the digest.

        """
        self.logger.info(
            "Get a yet unused brevity term for the digest from the database."
        )
        response = self.cursor.execute(
            "SELECT term, description FROM brevity_term WHERE used_in_digest = 0"
        )
        brevity_term = response.fetchone()

        if brevity_term is None:
            self.logger.info(
                "No unused brevity term found. Resetting 'used_in_digest'..."
            )
            self.cursor.execute("UPDATE brevity_term SET used_in_digest = 0")
            self.connection.commit()
            return self.get_brevity_terms_for_digest()

        self.logger.info(
            "Unused brevity term found. "
            "Updating 'used_in_digest' for brevity term"
        )
        self.cursor.execute(
            f"UPDATE brevity_term SET used_in_digest = 1 WHERE term = '{brevity_term[0]}'"
        )
        self.connection.commit()

        return brevity_term
