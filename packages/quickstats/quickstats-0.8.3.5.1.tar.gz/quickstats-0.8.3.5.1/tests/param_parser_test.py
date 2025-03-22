def test_param_str_and_filters():
    from quickstats.parsers import ParamParser
    parser = ParamParser(param_str="var1=0_10_0.5,var2=7_8_0.2")
    param_points = parser.get_internal_param_points()
    result_1cond_1param_numerical_match = parser.select_param_points(param_points, filter_expr="var1=2")
    assert result_1cond_1param_numerical_match == [{'var1': 2.0, 'var2': 7.0},
 {'var1': 2.0, 'var2': 7.2},
 {'var1': 2.0, 'var2': 7.4},
 {'var1': 2.0, 'var2': 7.6},
 {'var1': 2.0, 'var2': 7.8},
 {'var1': 2.0, 'var2': 8.0}]
    result_1cond_1param_wildcard_match = parser.select_param_points(param_points, filter_expr="var1=0.*")
    assert result_1cond_1param_wildcard_match == [{'var1': 0.0, 'var2': 7.0},
 {'var1': 0.0, 'var2': 7.2},
 {'var1': 0.0, 'var2': 7.4},
 {'var1': 0.0, 'var2': 7.6},
 {'var1': 0.0, 'var2': 7.8},
 {'var1': 0.0, 'var2': 8.0},
 {'var1': 0.5, 'var2': 7.0},
 {'var1': 0.5, 'var2': 7.2},
 {'var1': 0.5, 'var2': 7.4},
 {'var1': 0.5, 'var2': 7.6},
 {'var1': 0.5, 'var2': 7.8},
 {'var1': 0.5, 'var2': 8.0}]
    result_1cond_2param_wildcard_match = parser.select_param_points(param_points, filter_expr="var1=0.*,var2=*.2")
    assert result_1cond_2param_wildcard_match == [{'var1': 0.0, 'var2': 7.2}, {'var1': 0.5, 'var2': 7.2}]
    result_1cond_2param_numerical_match = parser.select_param_points(param_points, filter_expr="var1=5,var2=8")
    assert result_1cond_2param_numerical_match == [{'var1': 5.0, 'var2': 8.0}]
    result_2cond_2param_mixed_match = parser.select_param_points(param_points, filter_expr="var1=5.*,var2=7.4;var1=7.5")
    assert result_2cond_2param_mixed_match == [{'var1': 5.0, 'var2': 7.4},
 {'var1': 5.5, 'var2': 7.4},
 {'var1': 7.5, 'var2': 7.0},
 {'var1': 7.5, 'var2': 7.2},
 {'var1': 7.5, 'var2': 7.4},
 {'var1': 7.5, 'var2': 7.6},
 {'var1': 7.5, 'var2': 7.8},
 {'var1': 7.5, 'var2': 8.0}]