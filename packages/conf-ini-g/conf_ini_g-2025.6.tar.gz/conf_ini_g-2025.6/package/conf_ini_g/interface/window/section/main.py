"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from babelwidget.api.backend import backend_t
from babelwidget.api.widget import grid_lyt_h
from babelwidget.api.widget import group_h as group_wgt_h
from babelwidget.api.widget import label_h as label_wgt_h
from babelwidget.api.widget import stack_h as stack_wgt_h
from conf_ini_g.constant.section import INI_UNIT_SECTION
from conf_ini_g.interface.window.parameter.main import parameter_t as visual_parameter_t
from conf_ini_g.task.formatting import FormattedName
from conf_ini_g.type.dict import section_str_h
from conf_ini_g.type.parameter import prm_t as functional_parameter_t
from conf_ini_g.type.section import section_controlled_t as functional_controlled_t
from conf_ini_g.type.section import section_free_t as functional_free_t


@d.dataclass(repr=False, eq=False)
class _base_t:  # Cannot be abstracted.
    HEADER_NAMES: h.ClassVar[tuple[str]] = (
        "Parameter",
        "Type(s)",
        "Value",
        "Unit",
    )
    HEADER_STYLE: h.ClassVar[str] = "background-color: darkgray; padding-left: 5px;"

    functional: functional_free_t | functional_controlled_t
    library_wgt: group_wgt_h

    def __post_init__(self) -> None:
        """"""
        self.functional.interface = self

    @classmethod
    def NewWithName(
        cls,
        name: str,
        functional: functional_free_t | functional_controlled_t,
        backend: backend_t,
        /,
    ) -> h.Self:
        """"""
        output = cls(functional=functional, library_wgt=backend.group_t())

        if functional.__class__.is_controlled:
            controller = (
                f" ← {FormattedName(functional.controller[0])}."
                f"{FormattedName(functional.controller[1])}"
            )
        else:
            controller = ""
        formatted = FormattedName(name) + controller
        output.library_wgt.setTitle(formatted)

        return output

    @classmethod
    def Headers(cls, backend: backend_t, /) -> list[label_wgt_h]:
        """"""
        output = []

        for text in cls.HEADER_NAMES:
            header = backend.label_t(f'<font color="blue">{text}</font>')
            header.setStyleSheet(cls.HEADER_STYLE)
            output.append(header)

        return output


@d.dataclass(repr=False, eq=False)
class section_free_t(_base_t):

    @property
    def active_as_str_dict(self) -> section_str_h:
        """"""
        return {_key: _vle.interface.Text() for _key, _vle in self.functional.items()}

    @classmethod
    def New(
        cls,
        name: str,
        functional: functional_free_t,
        backend: backend_t,
        /,
    ) -> h.Self | None:
        """"""
        output = cls.NewWithName(name, functional, backend)

        parameters, layout = _VisualParameters(
            tuple(functional.prm_iterator), name == INI_UNIT_SECTION, backend
        )
        if parameters.__len__() == 0:
            return None

        for h_idx, header in enumerate(cls.Headers(backend)):
            layout.addWidget(header, 0, h_idx)
        output.library_wgt.setLayout(layout)

        return output


@d.dataclass(repr=False, eq=False)
class section_controlled_t(_base_t):
    subset_stack: stack_wgt_h = d.field(init=False)

    @property
    def active_as_str_dict(self) -> section_str_h:
        """"""
        output = {}

        controlling_value = self.functional.controller[2].interface.Text()
        if None in self.functional:
            values = (None, controlling_value)
        else:
            values = (controlling_value,)
        for value in values:
            output.update(
                {
                    _key: _vle.interface.Text()
                    for _key, _vle in self.functional[value].items()
                }
            )

        return output

    @classmethod
    def New(
        cls,
        name: str,
        functional: functional_controlled_t,
        backend: backend_t,
        /,
    ) -> h.Self | None:
        """"""
        output = cls.NewWithName(name, functional, backend)

        subset_stack = backend.stack_t()
        for (
            value,
            functional_s,
        ) in functional.prm_iterator_per_controlling_value:
            parameters, layout = _VisualParameters(functional_s, False, backend)
            if parameters.__len__() == 0:
                continue

            for h_idx, header in enumerate(cls.Headers(backend)):
                layout.addWidget(header, 0, h_idx)
            page = backend.base_t()
            page.setLayout(layout)
            subset_stack.addWidget(page)

        output.subset_stack = subset_stack

        # Curiously, the stacked widget cannot be simply declared as child of instance;
        # This must be specified through a layout.
        layout = backend.hbox_lyt_t()
        layout.addWidget(subset_stack)
        layout.setContentsMargins(0, 0, 0, 0)
        output.library_wgt.setLayout(layout)

        return output


any_section_h = section_free_t | section_controlled_t


def _VisualParameters(
    functional_s: h.Sequence[tuple[str, functional_parameter_t]],
    section_is_unit: bool,
    backend: backend_t,
    /,
) -> tuple[list[visual_parameter_t], grid_lyt_h]:
    """"""
    out_prm_s = []

    out_lyt = backend.grid_lyt_t()
    out_lyt.setAlignment(backend.ALIGNED_TOP)
    out_lyt.setColumnStretch(0, 4)
    out_lyt.setColumnStretch(1, 1)
    out_lyt.setColumnStretch(2, 8)
    out_lyt.setColumnStretch(3, 1)
    out_lyt.setContentsMargins(0, 0, 0, 0)

    for row, (name, functional) in enumerate(functional_s, start=1):
        parameter = visual_parameter_t.New(name, functional, backend)
        out_prm_s.append(parameter)

        out_lyt.addWidget(parameter.name, row, 0, alignment=backend.ALIGNED_RIGHT)
        out_lyt.addWidget(parameter.type, row, 1)
        out_lyt.addWidget(parameter.value.library_wgt, row, 2, 1, 2 - 1)
        if not section_is_unit:
            out_lyt.addWidget(parameter.unit, row, 3)

    return out_prm_s, out_lyt


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
