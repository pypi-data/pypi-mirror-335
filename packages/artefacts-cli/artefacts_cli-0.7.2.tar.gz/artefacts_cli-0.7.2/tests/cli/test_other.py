from artefacts.cli.other import generate_parameter_output
from artefacts.cli.parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON
import yaml
import json
import os


def test_generate_parameter_output(tmp_path):
    params = {"turtle/speed": 5}
    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_YAML
    with open(file_path) as f:
        out_params = yaml.load(f, Loader=yaml.Loader)
    os.remove(file_path)
    assert out_params == params

    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_JSON
    with open(file_path) as f:
        ros2_params = json.load(f)
    os.remove(file_path)
    assert ros2_params == params
