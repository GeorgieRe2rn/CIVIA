"""Synthetic aggregate fixtures only in tests; no production mock data."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from openapi_spec_validator import validate
from openapi_schema_validator import OAS30Validator
from jsonschema.exceptions import ValidationError
from civia_data.build import aggregate,validate_raw
from civia_data.train import FEATURES,PARAMS,features,split
from civia_data.common import ROOT
from civia_data.verify import verify
from sklearn.ensemble import RandomForestRegressor


@pytest.fixture
def raw():
    return pd.DataFrame([{'AELEC':2024,'FELECCION':'06/02/2024','EDOCVE':14,'EDONOM':'JALISCO','MPIOCVE':1,'MPIONOM':'Test agregado','SECCION':1,'SEXO':0,'EDAD':18,'LN':10,'SV':6,'NV':2,'NS':2}])


def test_unknown_is_not_abstention(raw):
    row=aggregate(raw,2024).iloc[0]
    assert row.participation_pct==75
    assert row.abstention_pct==25
    assert row.unknown_pct==20
    assert row.participation_lower_pct==60
    assert row.participation_upper_pct==80
    assert row.territory_id=='14001'
    assert row.election_date=='2024-06-02'


@pytest.mark.parametrize('sv,nv,expected',[(10,0,100),(0,10,0)])
def test_percentage_endpoints(raw,sv,nv,expected):
    raw.loc[0,['SV','NV','NS']]=[sv,nv,0]
    assert aggregate(raw,2024).iloc[0].participation_pct==expected


def test_duplicate_rejected(raw):
    with pytest.raises(ValueError,match='duplicad'):aggregate(pd.concat([raw,raw]),2024)


@pytest.mark.parametrize('column,value',[('SV',-1),('LN',11),('AELEC',2021),('EDOCVE',15),('EDAD',17),('SV',1.5),('NS',np.nan)])
def test_invalid_source_rejected(raw,column,value):
    raw=raw.astype({column:object});raw.loc[0,column]=value
    with pytest.raises((ValueError,TypeError)):aggregate(raw,2024)


def test_zero_known_does_not_impute(raw):
    raw.loc[0,['SV','NV','NS']]=[0,0,10]
    with pytest.raises(ValueError,match='denominador'):aggregate(raw,2024)


@pytest.fixture
def history():return pd.read_csv(ROOT/'data/processed/participation.csv',dtype={'territory_id':str})


def test_real_panel_quality(history):
    assert len(history)==750
    assert history.groupby('year').territory_id.nunique().eq(125).all()
    assert not history.duplicated(['territory_id','election_id']).any()
    assert (history.nominal_count==history.voted_count+history.not_voted_count+history.unknown_count).all()
    assert np.allclose(history.participation_pct+history.abstention_pct,100)
    assert history.participation_pct.between(0,100).all()
    assert set(history.loc[history.election_type.eq('federal_concurrente'),'year'])=={2012,2018,2024}
    assert set(history.loc[history.election_type.eq('federal_intermedia'),'year'])=={2009,2015,2021}


def test_no_target_features_and_chronological_split(history):
    panel=features(history);train,test=split(panel,2024)
    assert len(train)==375 and len(test)==125
    assert train.year.max()==2021 and test.year.min()==2024
    assert (panel.feature_max_year<panel.year).all()
    assert set(FEATURES).isdisjoint({'target','year','territory_id','nominal_count','participation_pct','abstention_pct'})
    changed=history.copy();changed.loc[changed.year.eq(2024),'abstention_pct']=99
    changed.loc[changed.year.eq(2024),'nominal_count']=999999
    modified=features(changed)
    pd.testing.assert_frame_equal(panel[FEATURES],modified[FEATURES])
    pd.testing.assert_frame_equal(train,split(modified,2024)[0])


def test_random_forest_reproducible(history):
    panel=features(history);train,test=split(panel,2024)
    a=RandomForestRegressor(**PARAMS).fit(train[FEATURES],train.target)
    b=RandomForestRegressor(**PARAMS).fit(train[FEATURES],train.target)
    np.testing.assert_array_equal(a.predict(test[FEATURES]),b.predict(test[FEATURES]))


def test_baseline_same_kind_and_prediction_limitations(history):
    panel=features(history)
    selected=panel[panel.year.eq(2024)].set_index('territory_id')
    prior=history[history.year.eq(2018)].set_index('territory_id')
    np.testing.assert_allclose(selected.sort_index().lag6_abstention_pct,prior.sort_index().abstention_pct)
    report=json.loads((ROOT/'ml/artifacts/evaluation.json').read_text(encoding='utf-8'))
    assert report['validation']['test_year']==2021
    assert report['interval'] is None and report['test_year']==2024


def test_contract_and_real_examples():
    contract=json.loads((ROOT/'contracts/openapi.yaml').read_text(encoding='utf-8'));validate(contract)
    index=json.loads((ROOT/'contracts/examples/index.json').read_text(encoding='utf-8'))
    for example in index:
        response=contract['paths'][example['path']][example['method']]['responses'][example['status']]
        schema=response['content']['application/json']['schema']
        # Resolve refs against components without deprecated RefResolver.
        def expand(value):
            if isinstance(value,dict):
                if '$ref' in value:return expand(contract['components']['schemas'][value['$ref'].split('/')[-1]])
                return {k:expand(v) for k,v in value.items()}
            if isinstance(value,list):return [expand(v) for v in value]
            return value
        data=json.loads((ROOT/'contracts/examples'/example['file']).read_text(encoding='utf-8'))
        OAS30Validator(expand(schema)).validate(data)


def test_no_future_prediction_request():
    contract=json.loads((ROOT/'contracts/openapi.yaml').read_text(encoding='utf-8'))
    schema=contract['components']['schemas']['PredictionRequest']
    OAS30Validator(schema).validate({'territory_id':'14041','election_id':'federal-2024'})
    with pytest.raises(ValidationError):OAS30Validator(schema).validate({'territory_id':'14041','election_id':'federal-2030'})


def test_committed_hashes():verify()
