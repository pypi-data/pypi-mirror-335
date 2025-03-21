"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from pathlib import Path as pl_path_t

from babelwidget.api.backend import backend_t
from babelwidget.api.widget import base_h as library_wgt_h
from babelwidget.api.widget import label_h as label_wgt_h
from babelwidget.api.widget import path_chooser_t
from babelwidget.api.widget import text_line_h as text_line_wgt_h
from conf_ini_g.constant.window import PATH_SELECTOR_WIDTH
from conf_ini_g.interface.window.parameter.value import value_wgt_a
from value_factory.api.catalog import path_kind_e, path_purpose_e, path_t
from value_factory.api.type import hint_t


@d.dataclass(repr=False, eq=False)
class path_wgt_t(value_wgt_a):
    """
    Cannot use slots (weak reference issue).
    """

    PostAssignmentFunction: h.Callable[[pl_path_t], None] | None
    library_wgt: library_wgt_h
    editable: bool
    backend_for_selection: backend_t
    type_: path_kind_e | None = d.field(init=False, default=None)
    path: text_line_wgt_h | label_wgt_h | None = d.field(init=False, default=None)
    _path_chooser: path_chooser_t | None = d.field(
        init=False, default=None
    )

    @classmethod
    def New(
        cls,
        stripe: hint_t,
        backend: backend_t,
        /,
        *,
        editable: bool = True,
        PostAssignmentFunction: h.Callable[[pl_path_t], None] | None = None,
    ) -> h.Self:
        """
        If stripe does not contain the necessary details, the target type is set to any and considered as input, and
        the selection button label ends with an exclamation point.
        """
        if editable:
            path = backend.text_line_t()
            messenger = path
        else:
            path = backend.label_t()
            messenger = None
        output = cls(
            messenger,
            "textChanged",
            backend,
            PostAssignmentFunction=PostAssignmentFunction,
            library_wgt=backend.base_t(),
            editable=editable,
            backend_for_selection=backend,
        )
        output.path = path

        annotation = stripe.FirstAnnotationWithType(path_t)
        if annotation is None:
            path_purpose = path_purpose_e.input
            path_kind = path_kind_e.any
        else:
            path_purpose = annotation.purpose
            path_kind = annotation.kind

        output.type_ = path_kind
        output._path_chooser = path_chooser_t.New(path_purpose.name, path_kind.name)

        if path_kind is path_kind_e.document:
            selector_label = "🗋"
        elif path_kind is path_kind_e.folder:
            selector_label = "📂"
        else:
            selector_label = "📂🗋"
        if path_purpose is path_purpose_e.input:
            selector_color = "green"
        elif path_purpose is path_purpose_e.output:
            selector_color = "red"
        else:
            selector_color = "blue"
        path_selector = backend.button_t(selector_label, parent=output.library_wgt)
        path_selector.SetFunction(output.SelectDocument)

        path_selector.setStyleSheet(f"color: {selector_color};")
        path_selector.setFixedWidth(PATH_SELECTOR_WIDTH)

        layout = backend.hbox_lyt_t()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(path)
        layout.addWidget(path_selector)
        output.library_wgt.setLayout(layout)

        return output

    def Assign(self, value: pl_path_t, _: h.Any, /) -> None:
        """"""
        value = _ValidStrValue(value, self.editable)
        self.path.setText(value)

    def Text(self) -> str | None:
        """
        /!\\ pathlib.Path("") == pathlib.Path(".").
        """
        return self.path.Text()

    def SelectDocument(self) -> None:
        """"""
        current_path = self.Text()
        current_doc = pl_path_t(current_path).resolve()

        # USed to use self.backend_for_selection.
        self._path_chooser.SetFolder(current_doc.parent)
        selection = self._path_chooser.NewSelected()
        if selection is None:
            return

        self.Assign(selection, None)
        # Put post-assignment call here instead of in the Assign method in case Assign
        # is also called at initialization time, in New, one day. Indeed, the
        # post-assignment task should have been done already, or will be done, when
        # instantiating the interface.
        if self.PostAssignmentFunction is not None:
            self.PostAssignmentFunction(selection)


def _ValidStrValue(value: pl_path_t, editable: bool, /) -> str:
    """"""
    if not editable:
        try:
            value = value.resolve(strict=True).relative_to(
                pl_path_t.home().resolve(strict=True)
            )
        except ValueError:
            # On Linux, this happens when home is a bind mount.
            pass

    return str(value)


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
