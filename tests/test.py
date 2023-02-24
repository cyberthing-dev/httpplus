
class test:
    def __init__(self,thing):
        self.thing=thing

    def __call__(self):
        print(f"{self.thing=}")

t = test("hello")

t()
