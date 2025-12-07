# Copyright 2025 Niklas Glienke

import shutil
import sqlite3
from pathlib import Path

import pytest

from cvw22_operations_officer.utils.database import Database


@pytest.fixture
def setup():
    """Set up the testcase with a temporary configuration directory"""
    tmp_dir = Path(__file__).resolve().parent / "tmp"
    database_path = tmp_dir / "cvw22_operations_officer.db"
    template_dir = Path(__file__).resolve().parent / "template"

    tmp_dir.mkdir(parents=False)
    open(database_path, "a").close()

    with open(template_dir / "schema.sql", "r") as f:
        schema_script = f.read()

    with open(template_dir / "brevity_term_test.sql", "r") as f:
        brevity_term_test_script = f.read()

    connection = sqlite3.connect(tmp_dir / "cvw22_operations_officer.db")
    cursor = connection.cursor()

    cursor.executescript(schema_script)
    cursor.executescript(brevity_term_test_script)

    yield tmp_dir

    connection.close()
    shutil.rmtree(tmp_dir)


def test_get_brevity_term_by_name_success(setup: Path) -> None:
    """Test function with a correct search term

    Args:
        setup (Path): The path to the temporary config directory

    """
    database = Database(setup)

    response = database.get_brevity_term_by_name("TEST TERM 1")

    assert len(response) == 1
    assert response[0][0] == "TEST TERM 1"
    assert response[0][1] == "TEST DESCRIPTION 1"


def test_get_brevity_term_by_name_partial(setup: Path) -> None:
    """Test function with only a part of the desired term

    Args:
        setup (Path): The path to the temporary config directory

    """
    database = Database(setup)

    response = database.get_brevity_term_by_name("TEST")

    assert len(response) == 3


def test_get_brevity_term_by_name_invalid(setup: Path) -> None:
    """Test function with an incorrect search term

    Args:
        setup (Path): The path to the temporary config directory

    """
    database = Database(setup)

    response = database.get_brevity_term_by_name("WRONG TERM")

    assert len(response) == 0


def test_get_brevity_terms_for_digest(setup: Path) -> None:
    """Test function whether brevity terms aren't used for digest yet

    Args:
        setup (Path): The path to the temporary config directory

    """
    database = Database(setup)

    response = database.get_brevity_terms_for_digest()

    assert len(response) == 2
