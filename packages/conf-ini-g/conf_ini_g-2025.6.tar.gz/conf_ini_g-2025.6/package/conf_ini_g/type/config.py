"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import textwrap as text
import typing as h
from pathlib import Path as path_t

from conf_ini_g.constant.console import MARGIN
from conf_ini_g.constant.section import INI_UNIT_SECTION
from conf_ini_g.interface.storage.config import INIConfig
from conf_ini_g.type.dict import config_str_h, config_typed_h, section_name_h
from conf_ini_g.type.parameter import ctl_t, prm_t
from conf_ini_g.type.property import ppt_t
from conf_ini_g.type.section import (
    section_controlled_t,
    section_definition_h,
    section_free_t,
)
from logger_36 import L
from value_factory.api.constant import ATOMIC_FACTORIES, UNSET
from value_factory.extension.hint import hint_h

config_definition_h = dict[section_name_h, section_definition_h]

_SECTION_TYPE = {False: section_free_t, True: section_controlled_t}


@d.dataclass(slots=True, repr=False, eq=False)
class config_t(dict[section_name_h, section_free_t | section_controlled_t]):

    definition: config_definition_h
    path: path_t | None = d.field(init=False, default=None)
    interface: h.Any = None

    @property
    def active_as_typed_dict(self) -> config_typed_h:
        """"""
        return {_snm: _sct.active_as_typed_dict for _snm, _sct in self.items()}

    def __post_init__(self) -> None:
        """"""
        controlled_sections = []
        for section in self.definition.values():
            for content in section.values():
                if isinstance(content, ctl_t):
                    controlled_sections.append(content.controlled_section)

        for name, section in self.definition.items():
            assert name.isidentifier(), name
            self[name] = _SECTION_TYPE[name in controlled_sections].New(section)

        for s_name, section in self.items():
            for p_name, content in section.items():
                if not isinstance(content, ctl_t):
                    continue

                target = self[content.controlled_section]  # Can "except".
                target.controller = (s_name, p_name, content)
                if (values := target.controlling_values) is not UNSET:
                    content.SetControllingValues(values)

        for section in self.values():
            if section.__class__.is_controlled:
                assert isinstance(section.controller, tuple), section.controller
            section.Issues(should_raise=True)

        # Wait for the config to be fully populated (optional plugin additions) before
        # checking if it has issues.

    def AddPluginParameter(
        self,
        s_name: str,
        p_name: str,
        /,
        *,
        hint: hint_h | None = None,
        default: h.Any = UNSET,
        controlling_value: str | None = None,
        short: str = "Plugin parameter",
        long: str = "This parameter is not part of the configuration definition. "
        'It was added programmatically in a "plugin" way.',
        basic: bool = True,
    ) -> None:
        """"""
        assert s_name.isidentifier(), s_name
        assert p_name.isidentifier(), p_name

        target = self[s_name]

        if not target.ppt.growable:
            raise RuntimeError(
                f"{s_name}.{p_name}: "
                f"Attempt to add an unspecified parameter to a section accepting none."
            )

        if not (target.__class__.is_controlled or (controlling_value is None)):
            raise RuntimeError(
                f"{s_name}.{p_name}<={controlling_value}: "
                f"Attempt to add a controlled parameter to an uncontrolled section."
            )

        if target.__len__() > 0:
            if target.__class__.is_controlled:
                error = p_name in target.prm_free_names
                if not (
                    error
                    or (controlling_value is None)
                    or (controlling_value not in target.controlling_values)
                ):
                    error = p_name in target[controlling_value]
            else:
                error = p_name in target
            if error:
                raise RuntimeError(
                    f"A parameter {p_name} already exists in section {s_name}."
                )

        parameter = prm_t(
            hint=hint,
            default=default,
            ppt=ppt_t(short=short, long=long, basic=basic),
        )

        if target.__class__.is_controlled:
            if controlling_value is None:
                if None in target:
                    target[None][p_name] = parameter
                else:
                    target[None] = {p_name: parameter}
            elif ((values := target.controlling_values) is not UNSET) and (
                controlling_value in values
            ):
                target[controlling_value][p_name] = parameter
            else:
                target[controlling_value] = {p_name: parameter}
                target.controller[2].AddControllingValue(controlling_value)
        else:
            target[p_name] = parameter

    def UpdateFromINI(self, path: str | path_t, /) -> list[str]:
        """"""
        ini_config = INIConfig(path)
        issues = self.UpdateFromDict(ini_config, should_interpret_values=True)
        if issues.__len__() > 0:
            self.path = None
            return issues

        self.path = path_t(path)
        return []

    def UpdateFromDict(
        self,
        config: config_str_h | config_typed_h,
        /,
        *,
        should_interpret_values: bool = True,
        should_update_interface: bool = True,
    ) -> list[str]:
        """
        should_interpret_values: Applies only to parameters not in the definition inside
        growable sections. The values of the parameters present in the definition are
        always interpreted in regard to their type hint.
        """
        output = []

        for s_name, section in config.items():
            if s_name not in self:
                if s_name == INI_UNIT_SECTION:
                    self[INI_UNIT_SECTION] = section_free_t.NewForUnits()
                else:
                    output.append(f"Section {s_name} does not exist.")
                    continue

            target = self[s_name]
            if s_name == INI_UNIT_SECTION:
                for name_full, value in section.items():
                    if "." in name_full:
                        if name_full not in target:
                            if (
                                should_interpret_values
                                and isinstance(value, str)
                                and not value.isidentifier()
                            ):
                                value = ATOMIC_FACTORIES.NewFromStr(value)
                            target[name_full] = prm_t.NewRuntime(
                                value, target.ppt.basic
                            )
                    else:
                        output.append(
                            f'Name {name_full} does not follow the format '
                            f'"section.parameter".'
                        )
            elif target.__class__.is_controlled:
                for p_name, value in section.items():
                    # The controlling value is not necessarily know yet, so all
                    # controlled parameters with a matching name will be set.
                    parameters = target.ControlledParameters(p_name, with_free=True)
                    if parameters.__len__() > 0:
                        for parameter in parameters:
                            output.extend(parameter.Assign(value))
                    else:
                        output.append(
                            f"Section {s_name} does not contain a parameter {p_name}."
                        )
            else:
                for p_name, value in section.items():
                    if p_name in target:
                        output.extend(target[p_name].Assign(value))
                    elif target.ppt.growable:
                        if p_name.isidentifier():
                            if should_interpret_values and isinstance(value, str):
                                value = ATOMIC_FACTORIES.NewFromStr(value)
                            target[p_name] = prm_t.NewRuntime(value, target.ppt.basic)
                        else:
                            output.append(
                                f"Parameter name {p_name} is not a valid identifier."
                            )
                    else:
                        output.append(
                            f"Section {s_name} does not contain a parameter {p_name}."
                        )

        if INI_UNIT_SECTION in self:
            for name_full, prm in self[INI_UNIT_SECTION].items():
                s_name, p_name = name_full.split(".", maxsplit=1)
                if not ((s_name in self) and (p_name in self[s_name])):
                    output.append(
                        f"No section {s_name} and/or no parameter {p_name} in section."
                    )
                    continue

                target = self[s_name]
                if target.__class__.is_controlled:
                    # All controlled parameters with a matching name will get the
                    # same unit.
                    parameters = target.ControlledParameters(p_name, with_free=True)
                else:
                    parameters = (target[p_name],)
                for parameter in parameters:
                    output.extend(parameter.SetUnit(prm.value))

        if should_update_interface and (self.interface is not None):
            self.interface.UpdateFromNewDict(output)

        return output

    def SyncWithInterface(self) -> None:
        """"""
        assert self.interface is not None
        self.UpdateFromDict(
            self.interface.active_as_str_dict, should_update_interface=False
        )

    def Reset(self) -> None:
        """"""
        self.clear()
        self.path = None
        self.__post_init__()

    def Issues(
        self,
        /,
        *,
        should_raise: bool = False,
        should_be_staged: bool = False,
        can_be_none: bool = False,
    ) -> list[str] | None | int | h.NoReturn:
        """
        should_raise_exception: If False, then returns the list of issues.
        """
        if self.__len__() == 0:
            message = "Empty specification."
            if should_raise:
                raise Exception(message)
            if should_be_staged:
                L.StageIssue(message)
                return 1
            return [message]

        output = []

        for s_name, section in self.items():
            if not section.__class__.is_controlled:
                continue

            c_s_name, c_p_name, _ = section.controller
            if c_s_name == s_name:
                output.append(f"A Section ({s_name}) cannot control itself.")
            elif self[c_s_name].__class__.is_controlled:
                output.append(
                    f'Section "{c_s_name}" of parameter '
                    f'"{c_p_name}", which controls section '
                    f'"{s_name}", is itself controlled'
                )

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

    def __str__(self) -> str:
        """"""
        output = []

        for name, section in self.items():
            output.append(f"[{name}]")
            output.extend(text.indent(str(section), MARGIN).splitlines())

        return "\n".join(output)

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
