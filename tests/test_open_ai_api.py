import csv
from datetime import date as real_date
from pathlib import Path

import pytest

import open_ai_api


def test_write_csv_preserves_field_order(tmp_path):
    rows = [
        {"first": 1, "second": 2},
        {"second": 3, "third": 4},
    ]
    output_file = tmp_path / "output.csv"

    open_ai_api._write_csv(output_file, rows)

    with open(output_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["first", "second", "third"]

        rows_read = list(reader)
        assert rows_read == [["1", "2", ""], ["", "3", "4"]]


def test_output_dir_and_images_dir_create_directories(monkeypatch, tmp_path):
    class DummyDate:
        @staticmethod
        def today():
            return real_date(2026, 5, 6)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(open_ai_api, "date", DummyDate)

    output_dir = open_ai_api._output_dir()
    images_dir = open_ai_api._images_dir()

    assert output_dir == tmp_path / "output" / "2026-05-06"
    assert output_dir.exists() and output_dir.is_dir()
    assert images_dir == tmp_path / "images"
    assert images_dir.exists() and images_dir.is_dir()
