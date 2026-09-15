from fastapi.testclient import TestClient
from api.main import app
from modules.architect.decompose import decompose_task
from importlib import import_module

def test_demo_and_session():
    client = TestClient(app)
    response = client.post('/api/decide', json={'goal': '示例'})
    assert response.status_code == 200
    result = response.json()
    assert '示例' in result['recommended_decision']
    assert result['monte_carlo']['p90_hours'] > result['monte_carlo']['p10_hours']
    assert client.get('/api/session/' + result['session_id']).json()['status'] == 'completed'

def test_plan_preserves_uncertainty_and_units():
    atoms = decompose_task({'id':'a','name':'a','optimistic':2,'most_likely':4,'pessimistic':12})
    assert atoms[0]['te'] == 5
    sim = import_module('shared.quant-engine.sim').monte_carlo_simulate(atoms, iterations=10000, seed=7)
    assert abs(sim['mean'] - 6) < 0.15
    result = TestClient(app).post('/api/decide', json={'goal':'a','plan':{'id':'a','name':'a','duration_estimate':4}}).json()
    assert result['monte_carlo']['mean_hours'] == 4

def test_invalid_plan_is_rejected():
    response = TestClient(app).post('/api/decide', json={'goal':'a','plan':{'id':'a','name':'a','optimistic':-1}})
    assert response.status_code == 422
