"""
Tests for the new JSON Schemas for the YAML formats.
"""
import json

from jsonschema import validate
import json
from pytest import fixture
from glob import glob
import os
import yaml


@fixture
def all_yaml_files():
    files = glob(os.path.join(os.path.dirname(__file__), "../instances/*.yaml"))
    return files


@fixture()
def schema():
    fn = os.path.join(os.path.dirname(__file__), "../../resources/schemas/dcop_file_format.json")
    with open(fn, 'r') as file:
        return json.load(file)


def test_validate_all(all_yaml_files, schema):
    for x in all_yaml_files:
        print(f"checking {x}")
        with open(x, 'r') as file:
            instance = yaml.safe_load(file)
        validate(json.loads(json.dumps(instance)), schema)
