from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from hypothesis import given
from hypothesis.strategies import sampled_from
from pytest import mark, param

from utilities.datetime import ZERO_TIME
from utilities.types import Dataclass, Duration, Number, PathLike


class TestDataClassProtocol:
    def test_main(self) -> None:
        TDataclass = TypeVar("TDataclass", bound=Dataclass)

        def identity(x: TDataclass, /) -> TDataclass:
            return x

        @dataclass(kw_only=True, slots=True)
        class Example:
            x: None = None

        _ = identity(Example())


class TestDuration:
    @given(x=sampled_from([0, 0.0, ZERO_TIME]))
    def test_success(self, *, x: Duration) -> None:
        assert isinstance(x, int | float | dt.timedelta)

    def test_error(self) -> None:
        assert not isinstance("0", int | float | dt.timedelta)


class TestNumber:
    @given(x=sampled_from([0, 0.0]))
    def test_ok(self, *, x: Number) -> None:
        assert isinstance(x, int | float)

    def test_error(self) -> None:
        assert not isinstance(None, int | float)


class TestPathLike:
    @mark.parametrize("path", [param(Path.home()), param("~")])
    def test_main(self, *, path: PathLike) -> None:
        assert isinstance(path, Path | str)

    def test_error(self) -> None:
        assert not isinstance(None, Path | str)
