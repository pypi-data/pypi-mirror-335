import pandas as pd
import numpy as np
import pytest

from pylluminator.dm import get_dmp, get_dmr, _get_model_parameters, get_top_dmrs


def test_dmp_ols(test_samples):
    probe_ids = test_samples.get_signal_df().reset_index()['probe_id'].sort_values()[:1000].tolist()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', probe_ids=probe_ids)
    assert dmps.loc['cg00000029_TC21', 'Intercept_estimate'] == pytest.approx(0.7574986020723979)  # Est_X.Intercept.
    assert dmps.loc['cg00000029_TC21', 'Intercept_p_value'] == pytest.approx(4.257315170037784e-06)  # Pval_X.Intercept.
    assert dmps.loc['cg00000029_TC21', 'sample_type[T.PREC]_estimate'] == pytest.approx(-0.7096783705055714)  # Est_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'sample_type[T.PREC]_p_value'] == pytest.approx(2.1946549071376195e-05)  # Pval_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'effect_size'] ==  pytest.approx(0.7096783705055714)  # Eff_sample_type

    dmps, contrasts = get_dmp(test_samples, '~ sample_type + sample_number', probe_ids=probe_ids)
    assert dmps.loc['cg00000029_TC21', 'Intercept_estimate'] == pytest.approx(0.8015912032375739) # Est_X.Intercept.
    assert dmps.loc['cg00000029_TC21', 'Intercept_p_value'] == pytest.approx(0.0003027740974405947)  # Pval_X.Intercept.
    assert dmps.loc['cg00000029_TC21', 'sample_type[T.PREC]_estimate'] == pytest.approx(-0.7096783705055711)  # Est_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'sample_type[T.PREC]_p_value'] == pytest.approx(0.00015479425278001256) # Pval_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'sample_number_estimate'] == pytest.approx(-0.02204630058258784)  # Est_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'sample_number_p_value'] == pytest.approx(0.30724222260281375) # Pval_sample_typeP
    assert dmps.loc['cg00000029_TC21', 'effect_size'] == pytest.approx(0.7096783705055711)  # Eff_sample_type

def test_dmp_mixedmodel(test_samples, caplog):
    probe_ids = test_samples.get_signal_df().reset_index()['probe_id'].sort_values()[:1000].tolist()
    test_samples.sample_sheet['sentrix_id'] = pd.NA

    # column with Nas
    caplog.clear()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', group_column='sentrix_id', probe_ids=probe_ids)
    assert 'The group column sentrix_id has NA values' in caplog.text
    assert dmps is None
    assert contrasts is None

    # non existing column
    caplog.clear()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', group_column='notfound', probe_ids=probe_ids)
    assert 'The group column notfound was not found' in caplog.text
    assert dmps is None
    assert contrasts is None

    # OK
    caplog.clear()
    test_samples.sample_sheet['sentrix_position'] = [name[-1:] for name in test_samples.sample_sheet['sample_name']]
    dmps, contrasts = get_dmp(test_samples, '~ sentrix_position', group_column='sentrix_position', probe_ids=probe_ids)
    assert 'ERROR' not in caplog.text
    assert dmps is not None
    assert contrasts is not None

def test_dmp_bad_sample_sheet(test_samples, caplog):
    # test missing value in factor column
    probe_ids = test_samples.get_signal_df().reset_index()['probe_id'].sort_values()[:1000].tolist()
    test_samples.sample_sheet.loc[3, 'sample_type'] = np.NAN
    caplog.clear()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', probe_ids=probe_ids)
    assert 'NA values where found in the sample_type column of the sample sheet' in caplog.text
    assert dmps is not None
    assert contrasts is not None

    # test missing value in group column
    probe_ids = test_samples.get_signal_df().reset_index()['probe_id'].sort_values()[:1000].tolist()
    test_samples.sample_sheet.loc[2, 'sample_number'] = np.NAN
    caplog.clear()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', group_column='sample_number', probe_ids=probe_ids)
    assert 'The group column sample_number has NA values' in caplog.text
    assert dmps is not None
    assert contrasts is not None

    # test missing sample_name column
    test_samples.sample_sheet = test_samples.sample_sheet.drop(columns='sample_name')
    caplog.clear()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type')
    assert 'the provided sample sheet must have a "sample_name" column' in caplog.text
    assert dmps is None
    assert contrasts is None


def test_dmp_wrong_formula(test_samples):
    # non existent factor column
    res = get_dmp(test_samples, '~ nonexistent_factor')
    assert len(res) == 2
    assert res[0] is None
    assert res[1] is None

def test_ols_na():
    nb_factors = 3
    params = _get_model_parameters([np.nan] * 5, pd.DataFrame(), ['factor'] * nb_factors)
    assert len(params) == 2 + nb_factors * 4
    assert np.isnan(params).all()

def test_dmr(test_samples):
    probe_ids = test_samples.get_signal_df().reset_index()['probe_id'].sort_values()[:1000].tolist()
    dmps, contrasts = get_dmp(test_samples, '~ sample_type', probe_ids=probe_ids)
    dmrs = get_dmr(test_samples, dmps, contrasts, probe_ids=probe_ids)
    assert max(dmrs.segment_id) == 516
    assert len(dmrs[dmrs.segment_id == 515]) == 3

    expected_values =['X', 152871744, 152871746, 515, 0.06386775794434923, 0.043502926826477106, 2.221477392945478e-07,
                       72.06726215266515, 0.8722137212753295, 0.012102773093109292, 0.06386775794434901,
                      -2.5416666348952717, -0.043502926826477106, 0.017115905850599335, 0.87221366, 0.8287108,
                      0.043502867, 151960303, 153792416, 0.04285787432065091, 0.055877280730965984, 0.7505345278316073,
                       0.055821167098151304, 0.75053453, 0.80635566, -0.05582112]
    assert dmrs.loc['cg00017004_BC21', ].values.tolist() == pytest.approx(expected_values)

    assert len(get_top_dmrs(dmrs, test_samples.annotation, 'sample_type[T.PREC]')) == 10
