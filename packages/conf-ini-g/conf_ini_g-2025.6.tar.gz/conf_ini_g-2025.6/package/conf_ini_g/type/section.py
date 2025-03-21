"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import textwrap as text
import typing as h

from conf_ini_g.constant.console import MARGIN
from conf_ini_g.type.dict import parameter_name_h, section_name_h, section_typed_h
from conf_ini_g.type.parameter import ctl_t, prm_t
from conf_ini_g.type.property import ppt_t
from logger_36 import L
from value_factory.api.constant import UNSET
from value_factory.api.type import unset_t

section_ppty_h = str
controlling_value_h = str

section_definition_h = dict[
    section_ppty_h | parameter_name_h | controlling_value_h,
    ppt_t | prm_t | dict[parameter_name_h, prm_t],
]


@d.dataclass(slots=True, repr=False, eq=False)
class section_free_t(dict[parameter_name_h, prm_t]):
    is_controlled: h.ClassVar[bool] = False  # To avoid having to use isinstance.

    ppt: ppt_t | None = None
    interface: h.Any = None

    @property
    def prm_iterator(self) -> h.Iterator[tuple[str, prm_t]]:
        """"""
        return iter(self.items())

    @property
    def active_parameters(self) -> tuple[[str, prm_t], ...]:
        """"""
        return tuple(self.items())

    @property
    def active_as_typed_dict(self) -> section_typed_h:
        """"""
        return {_key: _vle.value for _key, _vle in self.items()}

    def __post_init__(self) -> None:
        """"""
        if self.ppt is None:
            self.ppt = ppt_t()

    @classmethod
    def New(cls, definition: section_definition_h, /) -> h.Self:
        """"""
        output = cls()

        for name, content in definition.items():
            if isinstance(content, ppt_t):
                output.ppt = content
            else:
                if isinstance(content, prm_t):
                    assert name.isidentifier(), name
                else:
                    assert isinstance(name, str), name
                output[name] = content

        if output.ppt.growable is None:
            output.ppt.growable = output.__len__() == 0

        # Wait for the section to be fully initialized (optional plugin additions)
        # before checking if it has issues.

        return output

    @classmethod
    def NewForUnits(cls) -> h.Self:
        """"""
        output = cls()

        properties = output.ppt
        properties.short = "Parameter units"
        properties.long = (
            "Section to specify parameter units is the form "
            '"section.parameter = <SciPy_unit>" '
            "where <SciPy_unit> is a unit or SI prefix defined by the"
            "SciPy library. "
            "See: https://docs.scipy.org/doc/scipy/reference/constants.html"
        )
        properties.basic = True
        properties.growable = True

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
        return _Issues(self, should_raise, should_be_staged, can_be_none)

    def __str__(self) -> str:
        """"""
        return _AsStr(self)

    __repr__ = __str__


@d.dataclass(slots=True, repr=False, eq=False)
class section_controlled_t(
    dict[controlling_value_h | None, dict[parameter_name_h, prm_t]]
):
    """
    Free parameter: As opposed to controlled.

    There is an implicit constraint that if two parameters in two controlled subsets
    share the same name, they must have the same hint and unit.

    controller:
    - UNSET:                 The section is not functional yet,
    - s_name, p_name, ctl_t: The section is functional.
    """

    is_controlled: h.ClassVar[bool] = True  # To avoid having to use isinstance.

    ppt: ppt_t | None = None
    controller: tuple[section_name_h, parameter_name_h, ctl_t] | unset_t = d.field(
        init=False, default=UNSET
    )
    interface: h.Any = None

    @property
    def controlling_value(self) -> str:
        """"""
        return self.controller[2].value

    @property
    def controlling_values(self) -> tuple[str, ...] | unset_t:
        """"""
        if self.__len__() > 0:
            return tuple(sorted(_ for _ in self.keys() if _ is not None))
        return UNSET

    @property
    def prm_free_names(self) -> tuple[str, ...]:
        """"""
        if None in self:
            return tuple(self[None].keys())
        return ()

    @property
    def prm_iterator(self) -> h.Iterator[tuple[str, prm_t]]:
        """"""
        for subset in self.values():
            for name, parameter in subset.items():
                yield name, parameter

    @property
    def active_parameters(self) -> tuple[[str, prm_t], ...]:
        """"""
        if None in self:
            output = list(self[None].items())
        else:
            output = []
        output.extend(self[self.controlling_value].items())

        return tuple(output)

    @property
    def active_as_typed_dict(self) -> section_typed_h:
        """"""
        if None in self:
            output = {_key: _vle.value for _key, _vle in self[None].items()}
        else:
            output = {}
        output.update(
            {_key: _vle.value for _key, _vle in self[self.controlling_value].items()}
        )

        return output

    @property
    def prm_iterator_per_controlling_value(
        self,
    ) -> h.Iterator[tuple[str, tuple[tuple[str, prm_t], ...]]]:
        """"""
        if None in self:
            free_parameters = tuple(self[None].items())
        else:
            free_parameters = ()
        for value in self.controlling_values:
            yield value, free_parameters + tuple(self[value].items())

    def __post_init__(self) -> None:
        """"""
        if self.ppt is None:
            self.ppt = ppt_t()

    @classmethod
    def New(cls, definition: section_definition_h, /) -> h.Self:
        """"""
        output = cls()

        is_empty = definition.__len__() == 0
        is_empty_w_ppt = (definition.__len__() == 1) and isinstance(
            definition[tuple(definition.keys())[0]], ppt_t
        )
        # /!\\ ppt_t must not be a dict subclass, or has_dict_s becomes invalid.
        has_dict_s = any(isinstance(_, dict) for _ in definition.values())
        assert is_empty or is_empty_w_ppt or has_dict_s, (
            is_empty,
            is_empty_w_ppt,
            has_dict_s,
        )

        for name, content in definition.items():
            if isinstance(content, ppt_t):
                output.ppt = content
            elif isinstance(content, prm_t):
                assert name.isidentifier(), name
                if None in output:
                    output[None][name] = content
                else:
                    output[None] = {name: content}
            else:
                assert isinstance(name, str), name
                output[name] = content

        if output.ppt.growable is None:
            output.ppt.growable = output.__len__() == 0

        # Wait for the section to be fully initialized (optional plugin additions)
        # before checking if it has issues.

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
        return _Issues(self, should_raise, should_be_staged, can_be_none)

    def ControlledParameters(
        self, name: str | None, /, *, with_free: bool = False
    ) -> tuple[prm_t, ...] | tuple[tuple[str, prm_t], ...]:
        """
        name: None=all.
        """
        output = []

        values = self.controlling_values
        if with_free and (None in self):
            values += (None,)
        for value in values:
            subset = self[value]
            if name is None:
                output.extend(subset.items())
            elif name in subset:
                output.append(subset[name])

        return tuple(output)

    def __str__(self) -> str:
        """"""
        return _AsStr(self)

    __repr__ = __str__


def _Issues(
    section: section_free_t | section_controlled_t,
    should_raise: bool,
    should_be_staged: bool,
    can_be_none: bool,
    /,
) -> list[str] | None | int | h.NoReturn:
    """"""
    output = []

    basic = section.ppt.basic
    optional = section.ppt.optional
    growable = section.ppt.growable

    if not (section.ppt.basic or section.ppt.optional):
        output.append("Section is not basic but not optional.")

    if (section.__len__() == 0) and not growable:
        output.append("Empty non-growable section")

    if section.__len__() > 0:
        if section.__class__.is_controlled:
            # This might change if adding a runtime parameter can be done while
            # specifying a controlling value. However, adding a controlled parameter
            # will require checking that is does not have the name of a free one.
            if growable:
                output.append("A Controlled section cannot be growable.")

            if None in section:
                free = set(section[None].keys())
                if any(
                    free.intersection(section[_].keys()).__len__() > 0
                    for _ in section.controlling_values
                ):
                    output.append(
                        "Free parameter names cannot appear in the controlled subsets."
                    )

            for p_name, parameter in section.ControlledParameters(None):
                if not parameter.ppt.optional:
                    output.append(f'Controlled parameter "{p_name}" must be optional.')

            for p_name, parameter in section.prm_iterator:
                # Forbid controlling cascade to avoid cycles.
                if isinstance(parameter, ctl_t):
                    output.append(
                        f"Parameter {p_name} in controlled section "
                        f"cannot be itself a controller."
                    )

        n_parameters = 0
        n_basic_prms = 0
        for p_name, parameter in section.prm_iterator:
            n_parameters += 1
            if parameter.ppt.basic:
                n_basic_prms += 1

            if parameter.ppt.basic and not basic:
                output.append(f'Basic parameter "{p_name}" in advanced section')
            if optional and not parameter.ppt.optional:
                output.append(f'Mandatory parameter "{p_name}" in optional section')

        if basic and (n_parameters > 0) and (n_basic_prms == 0):
            output.append("Basic section without any basic parameters")

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


def _AsStr(section: section_free_t | section_controlled_t, /) -> str:
    """"""
    if section.ppt is None:
        # This should only happen in the recursive call triggered below.
        output = []
    else:
        output = ["Properties"]
        output.extend(text.indent(str(section.ppt), MARGIN).splitlines())
        if section.__class__.is_controlled:
            output.append(f"{MARGIN}Control: {section.controlling_value}")

    for name, content in section.items():
        if isinstance(content, prm_t):
            output.append(f"* {name}")
            output.extend(text.indent(str(content), MARGIN).splitlines())
        else:
            output.append(f"<= {name}")
            sub_section = section_free_t.New(content)
            sub_section.ppt = None  # /!\\ For convenient re-use of __str__.
            output.extend(text.indent(str(sub_section), MARGIN).splitlines())

    return "\n".join(output)


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
