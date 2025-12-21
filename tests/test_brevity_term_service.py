# Copyright 2025 Niklas Glienke

import pytest
import sqlite3

from cvw22_operations_officer.services.brevity_term_service import (
    BrevityTermService,
)
from cvw22_operations_officer.models.brevity_term_model import BrevityTerm


@pytest.fixture
def setup(tmp_path):
    db_path = tmp_path / "test.db"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE brevity_term ("
            "brevity_term_id INTEGER PRIMARY KEY, "
            "term TEXT NOT NULL, "
            "description TEXT NOT NULL, "
            "used_in_digest INTEGER NOT NULL)"
        )

        connection.executemany(
            "INSERT INTO 'brevity_term' "
            "('term', 'description', 'used_in_digest') VALUES (?, ?, ?)",
            [
                ("TERM 1", "[A/A] DESCRIPTION 1", 0),
                ("TERM 2 [number]", "[A/G] [MAR] DESCRIPTION 2", 0),
                ("TERM 3 EQ", "DESCRIPTION 3", 0),
                ("TERM EQ 4", "DESCRIPTION 4", 0),
                ("TERM EQ 5", "DESCRIPTION 5", 0),
                ("TERM 6", "DESCRIPTION 5", 0),
            ],
        )

    return db_path


def test_reset_used_in_digest(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute("UPDATE brevity_term SET used_in_digest = 1")

    brevity_term_service._reset_used_in_digest()

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        response = cursor.execute(
            "SELECT COUNT(used_in_digest) "
            "FROM brevity_term "
            "WHERE used_in_digest = 0"
        )
        num_of_unused_terms = response.fetchone()

    assert num_of_unused_terms[0] == 6


def test_set_used_in_digest(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    brevity_term_service._set_used_in_digest("TERM 6")

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        response = cursor.execute(
            "SELECT term FROM brevity_term WHERE used_in_digest = 1"
        )
        num_of_used_terms = response.fetchall()

    for term in num_of_used_terms[0]:
        assert term == "TERM 6"


def test_get_brevity_terms_by_term_valid(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    result = brevity_term_service.get_brevity_terms_by_term("EQ")

    assert len(result) == 3
    for term in result:
        assert isinstance(term, BrevityTerm)
        assert "EQ" in term.term


def test_get_brevity_terms_by_term_invalid(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    result = brevity_term_service.get_brevity_terms_by_term("NOT EQ")

    assert len(result) == 0


def test_get_brevity_terms_by_term_limit(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    result = brevity_term_service.get_brevity_terms_by_term("EQ", 2)

    assert len(result) == 2
    for term in result:
        assert isinstance(term, BrevityTerm)
        assert term.term in ("TERM 3 EQ", "TERM EQ 4", "TERM EQ 5")


def test_brevity_term_for_digest_all_unused(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    result = brevity_term_service.get_brevity_term_for_digest()

    assert isinstance(result, BrevityTerm)


def test_brevity_term_for_digest_all_used(setup):
    db_path = setup
    brevity_term_service = BrevityTermService(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute("UPDATE brevity_term SET used_in_digest = 1")

    result = brevity_term_service.get_brevity_term_for_digest()

    assert isinstance(result, BrevityTerm)
