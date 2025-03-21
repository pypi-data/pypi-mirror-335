"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from babelwidget.api.backend import backend_t
from babelwidget.api.widget import base_h as library_wgt_h
from babelwidget.api.widget import dropdown_choice_h as dropdown_choice_wgt_h
from babelwidget.api.widget import label_h as label_wgt_h
from babelwidget.api.widget import text_line_h as text_line_wgt_h
from conf_ini_g.catalog.choices import choices_wgt_t
from conf_ini_g.catalog.multitype import multi_type_wgt_t
from conf_ini_g.constant.window import TYPE_LABEL_WIDTH, TYPE_WIDGET_WIDTH
from conf_ini_g.interface.window.parameter.type import TypeSelector
from conf_ini_g.task.formatting import FormattedName
from conf_ini_g.task.translation import ValueWidgetTypeForType
from conf_ini_g.type.parameter import prm_t as functional_t
from value_factory.api.type import hint_t


@d.dataclass(repr=False, eq=False)
class parameter_t:
    """
    In order to leave the section widget put the name, type, and input widgets of each
    parameter in columns, parameter_t is not a container widget. Instead, it just stores
    its component widgets for later addition to a layout.
    """

    functional: functional_t
    #
    name: label_wgt_h = d.field(init=False)
    type: label_wgt_h | dropdown_choice_wgt_h = d.field(init=False)
    value: library_wgt_h = d.field(init=False)
    unit: text_line_wgt_h = d.field(init=False)

    def __post_init__(self) -> None:
        """"""
        self.functional.interface = self

    @classmethod
    def New(
        cls,
        name: str,
        functional: functional_t,
        backend: backend_t,
        /,
    ) -> h.Self:
        """"""
        output = cls(functional=functional)

        formatted = FormattedName(name)
        output.name = backend.label_t(formatted)

        comment = (
            f"{formatted}\n" f"{functional.ppt.short}.\n\n" f"{functional.ppt.long}."
        )
        output.name.setToolTip(comment)

        output.type, output.value = _TypeAndValueWidgetsForType(
            functional.hint, backend
        )
        output.unit = backend.text_line_t()

        style = "padding-right: 2px;"
        if functional.ppt.optional:
            style += "color: gray;"
        output.name.setStyleSheet(style)
        output.type.setStyleSheet(style)

        return output

    def SetVisible(self, visible: bool, /) -> None:
        """"""
        self.name.setVisible(visible)
        self.type.setVisible(visible)
        self.value.library_wgt.setVisible(visible)
        self.unit.setVisible(visible)

    def Text(self) -> str:
        """"""
        return self.value.Text()


def _TypeAndValueWidgetsForType(
    hint: hint_t, backend: backend_t, /
) -> tuple[library_wgt_h, library_wgt_h]:
    """"""
    if hint.is_union:
        hint_options = hint.elements
        type_wgt = TypeSelector(hint_options, backend)
        value_wgt = multi_type_wgt_t.NewForHints(hint_options, type_wgt, backend)
    else:
        template = hint.template_as_str
        if (length := template.__len__()) > TYPE_LABEL_WIDTH:
            shortened = "-" + template[(length - TYPE_LABEL_WIDTH + 1) :]
        else:
            shortened = template
        type_wgt = backend.label_t(shortened)
        if (nnts := hint.annotations) is None:
            nnts = ""
        else:
            nnts = "\n" + "\n".join(map(str, nnts))
        type_wgt.setToolTip(f"{template}{nnts}")
        if hint.is_literal:
            widget_type = choices_wgt_t
        else:
            widget_type = ValueWidgetTypeForType(hint)
        value_wgt = widget_type.New(hint, backend)

    type_wgt.setFixedWidth(TYPE_WIDGET_WIDTH)

    return type_wgt, value_wgt


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
