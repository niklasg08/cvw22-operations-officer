# Copyright 2025 Niklas Glienke

import sqlite3

import pytest

from cvw22_operations_officer.__main__ import setup_config_dir


def test_setup_config_dir_success(tmp_path):
    setup_config_dir(tmp_path)

    assert (tmp_path / "cvw22_operations_officer.db").exists()
    assert (tmp_path / "config.yaml").exists()


def test_setup_config_dir_valid_new_dir(tmp_path):
    config_dir = tmp_path / "config"

    setup_config_dir(config_dir)

    assert (config_dir / "cvw22_operations_officer.db").exists()
    assert (config_dir / "config.yaml").exists()


def test_setup_config_dir_invalid_new_dir(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.touch()

    with pytest.raises(NotADirectoryError):
        setup_config_dir(config_path)


def test_setup_config_dir_db_path_exists(tmp_path):
    db_path = tmp_path / "cvw22_operations_officer.db"
    db_path.touch()

    setup_config_dir(tmp_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        response = cursor.execute(
            "SELECT * FROM sqlite_master WHERE type='table';"
        )
        tables = response.fetchall()

        assert tables == []
