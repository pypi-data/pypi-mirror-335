class OrchestralTaskFailure(Exception):
    
    def __init__(self, error: str, trace: str,):
        self.trace = trace
        super().__init__(error)