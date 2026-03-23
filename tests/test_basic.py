# Minimal self-test for AtomicTask (pure Python version)
from core.schemas.atomic_task_py import AtomicTask

def test_construction():
    a = AtomicTask(id='t1', name='Test Task', duration_estimate=5.0, dependencies=['t0'])
    assert a.id == 't1'
    assert a.name == 'Test Task'
    assert a.duration_estimate == 5.0
    assert a.dependencies == ['t0']
    d = a.to_dict()
    assert d['id'] == 't1' and d['name'] == 'Test Task'
    print('OK')

if __name__ == '__main__':
    test_construction()
