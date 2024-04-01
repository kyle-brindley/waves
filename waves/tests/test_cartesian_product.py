"""Test CartesianProduct Class
"""

from unittest.mock import patch, call, mock_open
from contextlib import nullcontext as does_not_raise

import pytest
import numpy

from waves.parameter_generators import CartesianProduct
from waves._settings import _set_coordinate_key
from waves.exceptions import SchemaValidationError
from common import consistent_hash_parameter_check, self_consistency_checks, merge_samplers


class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class"""

    validate_input = {
        "good schema": (
            {'parameter_1': [1], 'parameter_2': (2,) , 'parameter_3': set([3, 4])},
            does_not_raise()
        ),
        "not a dict": (
            'not a dict',
            pytest.raises(SchemaValidationError)
        ),
        "bad schema int": (
            {'parameter_1': 1},
            pytest.raises(SchemaValidationError)
        ),
        "bad schema dict": (
            {'parameter_1': {'thing1': 1}},
            pytest.raises(SchemaValidationError)
        ),
        "bad schema str": (
            {'parameter_1': 'one'},
            pytest.raises(SchemaValidationError)
        ),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test_validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = CartesianProduct(parameter_schema)
            finally:
                pass

    generate_io = {
        'one_parameter': ({'parameter_1': [1, 2]},
                          numpy.array([[1], [2]])),
        'two_parameter': ({'parameter_1': [1, 2], 'parameter_2': ['a', 'b']},
                          numpy.array(
                              [[1, "a"],
                               [1, "b"],
                               [2, "a"],
                               [2, "b"]], dtype=object)),
        'ints and floats': ({'parameter_1': [1, 2], 'parameter_2': [3.0, 4.0]},
                            numpy.array(
                                [[1, 3.0],
                                 [1, 4.0],
                                 [2, 3.0],
                                 [2, 4.0]], dtype=object))
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, expected_array',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_generate(self, parameter_schema, expected_array):
        TestGenerate = CartesianProduct(parameter_schema)
        generate_array = TestGenerate._samples
        assert numpy.all(generate_array == expected_array)
        # Verify that the parameter set name creation method was called
        assert list(TestGenerate._parameter_set_names.values()) == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(len(expected_array))]
        parameter_set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
        assert numpy.all(parameter_set_names == expected_set_names)

    merge_test = {
        'single set unchanged':
            ({'parameter_1': [1]},
             {'parameter_1': [1]},
             # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
             numpy.array(
                 [[1]], dtype=object)),
        'single set and new set':
            ({'parameter_1': [1]},
             {'parameter_1': [2]},
             # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
             numpy.array(
                 [[2], [1]], dtype=object)),
        'new set':
            ({'parameter_1': [1, 2], 'parameter_2': [3.0], 'parameter_3': ['a']},
             {'parameter_1': [1, 2], 'parameter_2': [3.0, 4.0], 'parameter_3': ['a']},
             # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
             numpy.array(
                 [[2, 4.0, "a"],
                  [1, 3.0, "a"],
                  [1, 4.0, "a"],
                  [2, 3.0, "a"]], dtype=object)),
        'unchanged sets':
            ({'parameter_1': [1, 2], 'parameter_2': [3.0], 'parameter_3': ['a']},
             {'parameter_1': [1, 2], 'parameter_2': [3.0], 'parameter_3': ['a']},
             # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
             numpy.array(
                 [[1, 3.0, "a"],
                  [2, 3.0, "a"]], dtype=object)),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, expected_array', merge_test.values(), ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, expected_array):
        original_study, merged_study = merge_samplers(CartesianProduct, first_schema, second_schema, {})
        generate_array = merged_study._samples
        assert numpy.all(generate_array == expected_array)
        consistent_hash_parameter_check(original_study, merged_study)
        self_consistency_checks(merged_study)

    generate_io = {
        'one parameter yaml':
            ({"parameter_1": [1, 2]},
             'out',
             None,
             'yaml',
             2,
             [call("parameter_1: 1\n"),
              call("parameter_1: 2\n")]),
        'two parameter yaml':
            ({"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
             'out',
             None,
             'yaml',
             4,
             [call("parameter_1: 1\nparameter_2: a\n"),
              call("parameter_1: 1\nparameter_2: b\n"),
              call("parameter_1: 2\nparameter_2: a\n"),
              call("parameter_1: 2\nparameter_2: b\n")]),
        'two parameter yaml: floats and ints':
            ({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]},
             'out',
             None,
             'yaml',
             4,
             [call("parameter_1: 1\nparameter_2: 3.0\n"),
              call("parameter_1: 1\nparameter_2: 4.0\n"),
              call("parameter_1: 2\nparameter_2: 3.0\n"),
              call("parameter_1: 2\nparameter_2: 4.0\n")]),
        'one parameter one file yaml':
            ({"parameter_1": [1, 2]},
             None,
             'parameter_study.yaml',
             'yaml',
             1,
             [call("parameter_set0:\n  parameter_1: 1\n" \
                   "parameter_set1:\n  parameter_1: 2\n")]),
        'two parameter one file yaml':
            ({"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
             None,
             'parameter_study.yaml',
             'yaml',
             1,
             [call("parameter_set0:\n  parameter_1: 1\n  parameter_2: a\n" \
                   "parameter_set1:\n  parameter_1: 1\n  parameter_2: b\n" \
                   "parameter_set2:\n  parameter_1: 2\n  parameter_2: a\n" \
                   "parameter_set3:\n  parameter_1: 2\n  parameter_2: b\n")])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, output_file_template, output_file, output_type, file_count, ' \
                             'expected_calls',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_write_yaml(self, parameter_schema, output_file_template, output_file, output_type, file_count,
                        expected_calls):
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', return_value=False):
            TestWriteYAML = CartesianProduct(parameter_schema,
                                             output_file_template=output_file_template,
                                             output_file=output_file,
                                             output_file_type=output_type)
            TestWriteYAML.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)
