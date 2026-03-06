class T(): 
    def __init__(self, thing):
        setattr(self, "thing", thing)

t: T = T("h")

print(t.thing)