import os
import json
import datetime
from pathlib import Path

import pytest

from turbotape.records import (
    fetch_field,
    Record,
    CategoryMediator,
)


@pytest.fixture
def test_record():
    """
    Fixture for anything that needs test_record.json to be tested.
    """
    json_path = Path(__file__).parent / 'test_record.json'
    with open(json_path, mode='r') as fh:
        test_record = json.load(fh)
        return test_record


class TestCategoryMediator:

    @pytest.fixture()
    def my_field(self, test_record) -> dict:
        field = test_record['fields'][2]
        return field

    @pytest.fixture()
    def my_mediator(self) -> CategoryMediator:
        mediator = CategoryMediator()
        return mediator

    def test_update_category_str(self, my_field, my_mediator):
        value = 'Complete'
        res = my_mediator.update(my_field, value)
        assert res == [{ "value": \
            {
              "id": 48993,
              "text": "Complete",
              "color": "00866A",
              "means_completed": True
            }
        }]

    def test_fetch_category(self, my_mediator):
        assert \
            [(1, "Entered"), (2, "Accepted"), (3, "Rejected")] == \
            my_mediator.fetch(self.field, field_param='choices')
        assert \
            "Accepted" == \
            my_mediator.fetch(self.field)
        assert \
            "Accepted" == \
            my_mediator.fetch(self.field, field_param='active')['text']
        assert \
            2 == \
            my_mediator.fetch(self.field, field_param='active')['id']
        assert \
            "DCBD8" == \
            my_mediator.fetch(self.field, field_param='active')['color']


    def test_as_podio_dict(self, my_mediator):
        res = my_mediator.as_podio_dict(self.field)
        assert [2] == res


class TestFetchField:

    def test_get_field_not_found(self, test_record):
        assert None == fetch_field('does_not_exist', test_record)

    def test_get_field_with_underscore(self, test_record):
        # Dashes in external field where a problem when using them in e.g. 
        # template engines like Jinja2: {{ item.story_points }} would work 
        # while {{ item.story-points }} is illegal. Podio used '-' as a word 
        # seperator by default in external IDs (A field with the label 
        # "Story points" will be called "story-points" in Podio). Tape does the
        # "right" thing from  the beginning (using '_' instead of '-').
        assert '4.0000' == fetch_field('story_points', test_record)

    def test_get_text_field(self, test_record):
        assert "UI bug on login screen (Sample)" == fetch_field('title', test_record)

    def test_get_text_field_multiline(self, test_record):
        assert "<h1>Description Headline</h1><p>This is a descriptive text</p>" \
            == fetch_field('description', test_record)
        assert "Description HeadlineThis is a descriptive text" \
            == fetch_field('description__unformatted', test_record)

    def test_fetch_category_field(self, test_record):
        # Get all choices
        assert [(48992, "Not Started"), (48994, "In Progress"), (48993, "Complete")]\
            == fetch_field('status__choices', test_record)
        # Current status
        assert "In Progress" == fetch_field('status', test_record)
        # Get the currently selected option with text, ID and colour value.
        assert "In Progress" == fetch_field('status__active', test_record)['text']
        assert 48994 == fetch_field('status__active', test_record)['id']
        assert "DEA700" == fetch_field('status__active', test_record)['color']

    def test_fetch_app_field(self, test_record):
        assert [503454054] == fetch_field('projects', test_record)
        # TODO: Make these work, too.
        # assert 503454054 == fetch_field('projects__first', test_record)
        # assert 503454054 == fetch_field('projects__last', test_record)

    def test_fetch_calculation_field(self, test_record):
        assert "Hello,  John Doe" == fetch_field('calc', test_record)

    def test_fetch_date_field(self, test_record):
        assert '2018-07-27 01:00:00' == fetch_field('date', test_record)
        assert datetime.datetime(2018, 7, 27, 1, 0) == fetch_field('date__datetime', test_record)
        assert '2018-07-27 01:00:00' == fetch_field('date__start', test_record)

        # item[‘date__start_datetime’]
        assert datetime.datetime(2018, 7, 27, 1, 0) == fetch_field('date__start_datetime', test_record)
        assert datetime.datetime(2018, 7, 28, 1, 0) == fetch_field('date__end_datetime', test_record)

    def test_fetch_embed_field(self, test_record):
        assert \
            "http://www.newsletter-webversion.de/?c=0-v0yw-0-11xa&utm_source=newsletter&utm_medium=email&utm_campaign=02%2F2017+DT&newsletter=02%2F2017+DT" \
            == fetch_field('embed', test_record)


@pytest.fixture
def the_org_name():
    os.environ['TAPE_ORG_NAME'] = 'kollaborateure'
    return os.environ


class TestRecord:

    @pytest.fixture
    def my_record(self, test_record: dict) -> Record:
        return Record(test_record)
    
    def test_record_id(self, my_record):
        assert 111340631 == my_record.record_id
        assert 111340631 == my_record.item_id
        assert '111340631' == my_record.record_id__str
        assert '111340631' == my_record.record_id__str
    
    def test_files(self, my_record):
        """
        Try if we can get ALL files attached to a record somewhere.
        """
        res = my_record.files
        assert len(res) == 4
        assert res[0]['file_id'] == 4388
        assert res[0]['mimetype'] == 'image/png'
        for any_res in res:
            assert any_res.get('link') is not None
            assert any_res.get('download_url') is not None
            assert any_res.get('view_url') is not None

    def test_link_org_name_not_defined(self, my_record):
        """
        Try if we can get ALL files attached to a record somewhere.
        """
        assert f'https://tapeapp.com/TAPE_ORG_NAME/record/111340631' \
                == my_record.link

    @pytest.mark.skip(reason="enable when env var setting works inside one test")
    def test_link(self, my_record, the_org_name):
        """
        Try if we can get ALL files attached to a record somewhere.
        """
        assert f'https://tapeapp.com/TAPE_ORG_NAME/record/111340631' \
                == my_record.link
    
    def test__getitem__(self, my_record):
        assert "Bow of boat" == my_record['name']

    def test__setitem__(self, my_record):
        assert 0 == len(my_record._tainted)
        my_record['name'] = 'Bow of ship'
        # after setting the value, the number of tainted fields should go up.
        assert 1 == len(my_record._tainted)
        res = my_record.as_podio_dict(fields=my_record._tainted)
        assert "Bow of ship" == res['name']

    def test__setitem__textfield_none(self, my_record):
        assert 0 == len(my_record._tainted)
        my_record['name'] = None
        # after setting the value, the number of tainted fields should go up.
        assert 1 == len(my_record._tainted)
        res = my_record.as_podio_dict(fields=my_record._tainted)
        assert [] == res['name']

    def test_as_podio_dict(self, my_record):
        res = my_record.as_podio_dict(fields=['name'])
        assert "Bow of boat" == res['name']
