from fastapi.testclient import TestClient
from app.main import app

def test_health():
    assert TestClient(app).get('/health').json()['status']=='healthy'

def test_paper_position_lifecycle():
    with TestClient(app) as client:
        opened=client.post('/api/v1/positions',json={'ticker':'TEST','entry':100,'quantity':2,'stop':95,'target':108})
        assert opened.status_code==200
        closed=client.post(f"/api/v1/positions/{opened.json()['id']}/close",json={'exit_price':108})
        assert closed.json()['status']=='CLOSED'
        assert client.get('/api/v1/performance').json()['closed_trades']>=1
