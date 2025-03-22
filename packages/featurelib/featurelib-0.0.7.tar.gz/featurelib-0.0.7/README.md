`featurelib` contains tools to divide and maintain large code bases while providing better readability and easy extensibility and maintainability.

```python
from featurelib import feature, endpoint

class Logging(feature):
    def log(self, msg: str) -> None:
        # some logic here

    def log_to_terminal(self, msg: str) -> None:
        # some logic here


class Printing(feature):
    def print(self) -> None:
        print(self)


@endpoint
class App(Logging, Printing):
    def __init__(self) -> None:
        self.log('__init__ method.')
        self.print()
```