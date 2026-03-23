class AtomicTask:
    def __init__(self, id: str, name: str, duration_estimate: float, dependencies=None):
        self.id = id
        self.name = name
        self.duration_estimate = float(duration_estimate)
        self.dependencies = list(dependencies or [])
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration_estimate": self.duration_estimate,
            "dependencies": self.dependencies,
        }
    def __repr__(self):
        return f"AtomicTask(id={self.id!r}, name={self.name!r}, duration_estimate={self.duration_estimate!r}, dependencies={self.dependencies!r})"
