import json
import os
from pathlib import Path

import pytest

from turbotape.helpers import (
    upload_file,
    iterate_array,
    iterate_resource,
    intersection,
    union,
)

from turbotape.session import create_tape_session


@pytest.mark.skip(reason="no way of automatically testing this")
def test_upload_file():
    test_file = Path(__file__).parent / 'test-image.png'
    tape = create_tape_session()
    with open(test_file, mode="rb") as fh:
        raw_data = fh.read()
        res = upload_file(tape, 127782851, 'files', raw_data, 'test-image.png')
    print(res)


class TestIterateArray:

    def test_iterate_array(self):
        pass


class TestIterateResource:

    def test_iterate_resource(self):
        pass


class TestSetOpsResource:

    def test_intersection(self):
        res = intersection([1, 2], [2, 3], [2, 4, 5])
        assert 1 == len(res)
        assert 2 == res[0]

    def test_union(self):
        res = union([1, 2], [2, 3], [2, 4, 5])
        assert 5 == len(res)
        assert 1 == res[0]