"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import textwrap as text
import typing as h

import scipy.constants as unit
from conf_ini_g.constant.console import MARGIN
from conf_ini_g.task.conversion import ValueInStandardUnit
from conf_ini_g.type.dict import section_name_h
from conf_ini_g.type.property import ppt_t
from logger_36 import L
from value_factory.api.catalog import annotation_a
from value_factory.api.constant import UNSET
from value_factory.api.extension import hint_h
from value_factory.api.task import NewCastValue
from value_factory.api.type import (
    hint_t,
    invalid_t,
    unset_t,
    value_passed_h,
    value_wanted_h,
)

MustRespect_h = h.Callable[[value_wanted_h], bool]


@d.dataclass(slots=True, repr=False, eq=False)
class prm_t:
    hint: hint_h | hint_t | annotation_a = h.Any
    unit_name: str | None = None
    unit_factor: float | None = None
    default: value_wanted_h = UNSET
    _value: value_wanted_h = d.field(init=False, default=UNSET)
    must: MustRespect_h | tuple[MustRespect_h, ...] | None = None
    ppt: ppt_t | None = None
    interface: h.Any = None

    @property
    def value(self) -> value_wanted_h | invalid_t | unset_t:
        """"""
        if self._value is UNSET:
            if self.default is UNSET:
                return UNSET
            output = self.default
        else:
            output = self._value

        if self.unit_factor is None:
            return output

        return ValueInStandardUnit(output, self.unit_name, self.unit_factor)

    def __post_init__(self) -> None:
        """"""
        assert not isinstance(self.default, invalid_t)

        if not isinstance(self.hint, hint_t):
            self.hint = hint_t.New(self.hint)

        if self.must is None:
            self.must = ()
        elif isinstance(self.must, h.Callable):
            self.must = (self.must,)
        elif not isinstance(self.must, tuple):
            self.must = tuple(self.must)

        if self.ppt is None:
            self.ppt = ppt_t()
        self.ppt.optional = self.default is not UNSET

        self.Issues()

    @classmethod
    def NewRuntime(cls, value: h.Any, basic: bool, /) -> h.Self:
        """
        Runtime means "not part of the configuration definition".
        """
        output = cls(
            hint=type(value),
            ppt=ppt_t(
                short="Runtime parameter",
                long="This parameter is not part of the configuration definition. "
                "It was encountered in an INI configuration and added programmatically.",
                basic=basic,
            ),
        )
        output._value = value
        return output

    def Issues(
        self,
        /,
        *,
        should_raise: bool = False,
        should_be_staged: bool = False,
        can_be_none: bool = False,
    ) -> list[str] | None | int | h.NoReturn:
        """"""
        output = []

        if self.ppt.optional:
            converted, issues = NewCastValue(self.default, self.hint)
            if issues.__len__() > 0:
                output.extend(issues)
            else:
                self.default = converted
                for must in self.must:
                    if not must(self.default):
                        output.append(f"{must.__name__}({self.default}) is False.")
        elif not self.ppt.basic:
            output.append("Parameter is not basic but not optional.")

        if (n_output := output.__len__()) > 0:
            if should_raise:
                raise Exception("\n".join(output))
            if should_be_staged:
                for element in output:
                    L.StageIssue(element)
                return n_output
            return output

        if should_raise:
            return None
        if should_be_staged:
            return 0
        if can_be_none:
            return None
        return []

    def Assign(self, value: value_passed_h | invalid_t | unset_t, /) -> list[str]:
        """"""
        if isinstance(value, invalid_t | unset_t):
            self._value = value
            return [f"Unexpected value {value}."]

        converted, issues = NewCastValue(value, self.hint)
        if issues.__len__() > 0:
            return issues

        does_not_respect = ", ".join(
            getattr(_, "__name__", str(_)) for _ in self.must if not _(converted)
        )
        if does_not_respect.__len__() > 0:
            return [f"{converted} does not respect {does_not_respect}."]

        self._value = converted

        return []

    def SetUnit(self, passed: str | int | float, /) -> list[str]:
        """"""
        if isinstance(passed, int | float):
            self.unit_name = f"<unit*{passed}>"
            self.unit_factor = passed
            return []

        unit_as_float = getattr(unit, passed, None)
        if unit_as_float is None:
            return [
                f"Unit {passed} is not defined by the SciPy library. "
                f"See: https://docs.scipy.org/doc/scipy/reference/constants.html"
            ]

        self.unit_name = passed
        self.unit_factor = unit_as_float
        return []

    def __str__(self) -> str:
        """"""
        type_options = self.hint
        if isinstance(type_options, type):
            type_options = type_options.__name__

        if self._value is UNSET:
            if self.default is UNSET:
                value = ""
            else:
                value = (
                    f"Value: {self.default}:{type(self.default).__name__} (default)\n"
                )
        else:
            if self.unit_factor is None:
                unit_name = ""
            else:
                unit_name = f" {self.unit_name}"
            value = f"Value: {self._value}{unit_name}:{type(self._value).__name__}\n"

        must = ", ".join(getattr(_, "__name__", str(_)) for _ in self.must)
        return (
            f"Properties:\n{text.indent(str(self.ppt), MARGIN)}\n"
            f"Type options: {type_options}\n"
            f"{value}"
            f"Must respect: {must}"
        )

    __repr__ = __str__


@d.dataclass(slots=True, repr=False, eq=False)
class ctl_t(prm_t):
    controlled_section: section_name_h = ""

    def __post_init__(self) -> None:
        """
        A controller must not have an explicit default value; The default value is set
        as the first non-None key of the controlled section.
        """
        prm_t.__post_init__(self)

        assert self.hint.type is h.Any
        assert (self.unit_name is None) and (self.unit_factor is None)
        assert self.default is UNSET
        assert self.must == ()
        assert not self.ppt.optional
        assert isinstance(self.controlled_section, str) and (
            self.controlled_section.__len__() > 0
        )

        self.hint.type = str

    def AddControllingValue(self, value: str, /) -> None:
        """"""
        assert isinstance(value, str), value

        if self.hint.is_literal:
            assert self.hint.is_str_literal, self.hint
            self.hint.AddLiteral(value)
        else:
            assert self.hint.type is str, self.hint
            self.hint = hint_t.New(h.Literal[(value,)])

        if self._value is UNSET:
            self._value = value

    def SetControllingValues(self, values: tuple[str, ...], /) -> None:
        """"""
        values = tuple(sorted(values))
        self.hint = hint_t.New(h.Literal[values])
        self._value = values[0]

    def __str__(self) -> str:
        """"""
        return f"{prm_t.__str__(self)}\nControls: {self.controlled_section}"

    __repr__ = __str__


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
