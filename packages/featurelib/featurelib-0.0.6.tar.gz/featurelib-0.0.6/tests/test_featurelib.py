

from featurelib import feature, requires, optimize, endpoint
from featurelib.abc import feature_info, validate
import pytest

class feature_1(feature):
    def method_1(self) -> None:
        print(1)

class feature_2(feature):
    def method_1(self) -> None:
        print(2, 1)

class feature_3(feature):
    def method_3(self) -> None:
        print(3)

def test_feature_creation():
    class feature_1(feature):
        def method_1(self) -> None:
            print(1)

    class feature_2(feature):
        def method_1(self) -> None:
            print(2, 1)

    class feature_3(feature):
        def method_3(self) -> None:
            print(3)
    
    assert True


@pytest.mark.filterwarnings('ignore::SyntaxWarning')
def test_feature_inheritence():
    class feature_1(feature):
        def method_1(self) -> None:
            print(1)

    class feature_2(feature):
        def method_1(self) -> None:
            print(2, 1)

    class feature_3(feature):
        def method_3(self) -> None:
            print(3)
    
    class feature_4(feature_1):
        def abc(self) -> None: ...
    
    class feature_5(feature_4, feature):
        def abs(self) -> None: ...
    
    @endpoint
    class end(feature_2, feature_3):
        @requires(feature_3)
        def process(self) -> None:
            self.method_3()

    assert validate(end)

    @endpoint
    class end2(feature_2):
        @requires(feature_3)
        def process(self) -> None: ...
    
    assert validate(end2) is False

    @endpoint
    class end3(feature_1, feature_2):
        def method_1(self) -> None:
            return super().method_1()
    
    assert validate(end3) is False

    try:
        @endpoint
        class end4(feature_4, feature_5):
            ...
        assert validate(end4) is False
    except TypeError: # ABC catches the error first
        assert True