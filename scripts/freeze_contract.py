"""G1 adds real scientific metadata and examples before any API consumer exists."""
import json
from pathlib import Path
import pandas as pd
from civia_data.common import ROOT, write_json

r=ROOT
p=r/'contracts/openapi.yaml'
c=json.loads(p.read_text(encoding='utf-8'))
c['info']={'title':'CIVIA API - contrato G1','version':'1.1.0','description':'Contrato G1 para revisión de Lluvia. Cobertura Jalisco/municipios INE; CCPC 2009-2024; tasas entre condición conocida SV+NV, NS separado. Predicción: backtest 2024, no pronóstico futuro. API aún no implementada.'}
s=c['components']['schemas']
string={'type':'string'}
percentage={'type':'number','minimum':0,'maximum':100}
integer={'type':'integer','minimum':0}
def add(schema,props):
 s[schema]['properties'].update(props)
 s[schema]['required']=list(s[schema]['properties'])
add('Territory',{'state_id':{'type':'string','enum':['14']},'code_system':{'type':'string','enum':['INE_EDOCVE_MPIOCVE']}})
s['Territory']['properties']['id']={'type':'string','pattern':'^14[0-9]{3}$','description':'INE EDOCVE (2) + MPIOCVE (3). No asumir clave INEGI.'}
s['Territory']['properties']['level']={'type':'string','enum':['municipio']}
add('Observation',{'territory_id':string,'election_date':{'type':'string','format':'date'},'election_type':{'type':'string','enum':['federal_concurrente','federal_intermedia']},'nominal_count':integer,'voted_count':integer,'not_voted_count':integer,'unknown_count':integer,'known_count':integer,'unknown_pct':percentage,'participation_lower_pct':percentage,'participation_upper_pct':percentage,'denominator':{'type':'string','enum':['SV+NV']}})
s['Observation']['properties']['participation_pct']['description']='100*SV/(SV+NV); no representa SV/LN. NS se presenta separado.'
s['Observation']['properties']['participation_lower_pct']['description']='100*SV/LN: extremo aritmético por faltantes, NO intervalo estadístico.'
s['Observation']['properties']['participation_upper_pct']['description']='100*(SV+NS)/LN: extremo aritmético por faltantes, NO intervalo estadístico.'
add('Prediction',{'territory_id':string,'election_id':{'type':'string','enum':['federal-2024']},'participation_pct':percentage,'strategy':{'type':'string','enum':['random_forest','baseline_lag6']},'evaluation_mode':{'type':'string','enum':['retrospective_holdout']}})
for name in ['PredictionRequest','ScenarioRequest']:
 s[name]['additionalProperties']=False
 s[name]['properties']['territory_id']={'type':'string','pattern':'^14[0-9]{3}$'}
 s[name]['properties']['election_id']={'type':'string','enum':['federal-2024'],'description':'Solo backtest 2024; otros objetivos requieren nuevo artefacto y validación.'}
add('Scenario',{'territory_id':string,'election_id':{'type':'string','enum':['federal-2024']},'base_status':{'type':'string','enum':['predicho']},'base_evaluation_mode':{'type':'string','enum':['retrospective_holdout']}})
s['Election']={'type':'object','required':['election_id','year','election_date','election_type'],'properties':{'election_id':string,'year':{'type':'integer'},'election_date':{'type':'string','format':'date'},'election_type':{'type':'string','enum':['federal_concurrente','federal_intermedia']}}}
def ref(name):return {'$ref':'#/components/schemas/'+name}
def envelope(data):return {'type':'object','required':['meta','data','sources'],'properties':{'meta':ref('Meta'),'data':data,'sources':{'type':'array','items':ref('Source')}}}
s['Meta']['properties']['warnings']={'type':'array','items':string}
s['Meta']['required'].append('warnings') if 'warnings' not in s['Meta']['required'] else None
c['paths']['/api/elecciones']={'get':{'summary':'Catálogo de las seis elecciones disponibles','responses':{'200':{'description':'Catálogo','content':{'application/json':{'schema':envelope({'type':'array','items':ref('Election')})}}}}}}
for path,methods in c['paths'].items():
 for method,op in methods.items():
  op['operationId']=method+'_'+path.split('/')[-1]
  if path=='/api/elecciones':
   for status in ['422','503']:op['responses'][status]={'description':'Error estructurado','content':{'application/json':{'schema':ref('Error')}}}
c['paths']['/api/mapa']['get']['description']='G1 no incluye geometrías verificadas. Hasta contar con correspondencia geográfica documentada responder 503 DATA_UNAVAILABLE; nunca inventar GeoJSON.'
c['paths']['/api/predicciones']['post']['description']='Servir predictions_2024.json con metadatos y advertencia de backtest. No usa observación 2024 como input. Solo 2024, otras elecciones 422. Modelo no disponible 503. Nunca entrenar por petición.'
c['paths']['/api/escenarios']['post']['description']='Base = 100 - abstención predicha del backtest 2024. Final=clamp(base+delta_pp,0,100); clamped indica si se saturó. Sin causalidad. Artefacto ausente:503.'
write_json(p,c)
# Real example snapshots, NOT mocked production numbers.
history=pd.read_csv(r/'data/processed/participation.csv',dtype={'territory_id':str})
territories=json.loads((r/'data/processed/territories.json').read_text(encoding='utf-8'))
sources=json.loads((r/'data/sources.lock.json').read_text(encoding='utf-8'))
metadata=json.loads((r/'data/processed/metadata.json').read_text(encoding='utf-8'))
preds=json.loads((r/'ml/artifacts/predictions_2024.json').read_text(encoding='utf-8'))
chosen=next(t for t in territories if t['name']=='Guadalajara')
id=chosen['id']
stamp=max(t['retrieved_at'] for t in sources)
def wrap(data,status,years=[]):
 return {'meta':{'source_version':metadata['source_version'],'timestamp':stamp,'data_status':status,'warnings':metadata['warnings']},'data':data,'sources':[{k:t[k] for k in ['id','url','title','retrieved_at']} for t in sources if t['year'] in years]}
obs=history[history.territory_id.eq(id)].to_dict('records')
obs=[{k:v for k,v in row.items() if k in s['Observation']['properties']} for row in obs]
pred=next(t for t in preds if t['territory_id']==id)
base=100-pred['abstention_pct'];final=min(100,max(0,base+3))
examples={
 'health':('/api/health','get',wrap({'status':'ok','version':'0.1.0','ai_enabled':False},'no_aplica')),
 'territorios':('/api/territorios','get',wrap(territories,'no_aplica',[2024])),
 'elecciones':('/api/elecciones','get',wrap(json.loads((r/'data/processed/elections.json').read_text(encoding='utf-8')),'no_aplica',[y['year'] for y in sources])),
 'participacion':('/api/participacion','get',wrap(obs,'observado',[y['year'] for y in sources])),
 'predicciones':('/api/predicciones','post',wrap(pred,'predicho',[y['year'] for y in sources])),
 'escenarios':('/api/escenarios','post',wrap({'territory_id':id,'election_id':'federal-2024','base_participation_pct':base,'final_participation_pct':final,'final_abstention_pct':100-final,'delta_pp':3,'clamped':False,'label':'Simulación hipotética','base_status':'predicho','base_evaluation_mode':'retrospective_holdout'},'simulado',[y['year'] for y in sources])),
 'asistente':('/api/asistente','post',wrap({'answer':'Este ejemplo usa registros de condición conocida (SV+NV). Los no especificados se muestran por separado.','mode':'determinista','source_ids':['ine-ccpc-2024-jal']},'no_aplica',[2024])),
}
index=[]
for name,(path,method,value) in examples.items():
 write_json(r/f'contracts/examples/{name}.json',value)
 index.append({'file':name+'.json','path':path,'method':method,'status':'200'})
error={'meta':wrap(None,'no_aplica')['meta'],'error':{'code':'DATA_UNAVAILABLE','message':'No se dispone de geometrías verificadas en G1'}}
write_json(r/'contracts/examples/mapa_no_disponible.json',error)
index.append({'file':'mapa_no_disponible.json','path':'/api/mapa','method':'get','status':'503'})
write_json(r/'contracts/examples/index.json',index)
print(f'Contrato 1.1.0 preparado: {len(c["paths"])} endpoints; ejemplo {id}, Guadalajara')
