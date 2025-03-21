"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import inspect as nspt
import typing as h
from pathlib import Path as path_t

from babelwidget.backend.generic.path_chooser import path_chooser_t
from babelwidget.api.backend import backend_t
from babelwidget.api.widget import base_h as library_wgt_h
from conf_ini_g.interface.storage.config import SaveConfigToINIDocument
from conf_ini_g.interface.window.config.action import ActionButtonsLayout
from conf_ini_g.interface.window.config.advanced import AdvancedModeLayout
from conf_ini_g.interface.window.config.title import TitleLayout
from conf_ini_g.interface.window.section.collection import SectionsAndCategories
from conf_ini_g.task.formatting import FormattedName
from conf_ini_g.type.config import config_t as functional_t
from conf_ini_g.type.dict import config_str_h, config_typed_h
from logger_36 import L
from value_factory.api.type import invalid_t, unset_t


@d.dataclass(repr=False, eq=False)
class config_t:
    """
    The class cannot use slots because it disables weak referencing, which is required.
    See error message below when using slots:
    TypeError: cannot create weak reference to 'config_t' object
    [...]
    File "[...]conf_ini_g/catalog/interface/window/backend/pyqt5/widget/choices.py", line 41, in SetFunction
        self.clicked.connect(function)
        │                    └ <bound method config_t.ToggleAdvancedMode of <conf_ini_g.interface.window.config.config_t object at [...]>>
        └ <conf_ini_g.catalog.interface.window.backend.pyqt5.widget.choices.radio_choice_wgt_h object at [...]>

    Widget might not cooperate well with list, in which case Python raises the
    following exception: TypeError: multiple bases have instance lay-out conflict
    To be safe, "sections" is a field instead of being part of the class definition.

    _widget: Both an access for interacting with widgets, and a reference keeper to
    prevent autonomous widgets from loosing their "liveness".
    """

    functional: functional_t
    UpdateHistory: h.Callable[[path_t | str], None] | None
    #
    backend: backend_t
    library_wgt: library_wgt_h
    #
    Action: h.Callable[[config_typed_h], None] | None = None
    #
    _widget: dict[str, library_wgt_h] = d.field(init=False, default_factory=dict)

    @property
    def active_as_str_dict(self) -> config_str_h:
        """"""
        return {
            _key: _vle.interface.active_as_str_dict
            for _key, _vle in self.functional.items()
        }

    def __post_init__(self) -> None:
        """"""
        self.functional.interface = self

        if not ((self.functional.path is None) or (self.UpdateHistory is None)):
            self.UpdateHistory(self.functional.path)

    @classmethod
    def New(
        cls,
        title: str | None,
        functional: functional_t,
        backend: backend_t,
        /,
        *,
        history: h.Sequence[str] | None = None,
        UpdateHistory: h.Callable[[path_t | str], None] | None = None,
        action: tuple[str, h.Callable[[config_typed_h], None]] = None,
        advanced_mode: bool = False,
    ) -> h.Self:
        """"""
        if action is None:
            kwargs = {}
        else:
            kwargs = {"Action": action[1]}

        output = cls(
            functional=functional,
            backend=backend,
            library_wgt=backend.base_t(),
            UpdateHistory=UpdateHistory,
            **kwargs,
        )

        path_ini = functional.path

        if path_ini is not None:
            as_str = str(path_ini)
            if history is None:
                history = (as_str,)
            elif as_str not in history:
                history = list(history)
                history.append(as_str)

        # --- Top-level widgets
        (
            title_lyt,
            ini_path_wgt,
            history_button,
            history_menu,
            close_button,
        ) = TitleLayout(
            title,
            functional,
            history,
            backend,
            path_ini,
            functional.UpdateFromINI,
            output.library_wgt.close,
        )
        advanced_mode_lyt, adv_mode_wgt = AdvancedModeLayout(
            advanced_mode, backend, output.ToggleAdvancedMode
        )
        button_lyt, action_button, action_wgt_s = ActionButtonsLayout(
            action,
            path_ini is not None,
            backend,
            output.ShowInConsole,
            output.SaveConfig,
            output.LaunchAction,
            output.library_wgt.close,
        )
        output._widget["path_ini"] = ini_path_wgt
        output._widget["history_button"] = history_button
        output._widget["history_menu"] = history_menu
        output._widget["adv_mode"] = adv_mode_wgt
        output._widget["action"] = action_button
        output._widget["action_buttons"] = action_wgt_s
        output._widget["close"] = close_button

        # --- Sections
        category_selector = SectionsAndCategories(functional, None, backend)
        output._widget["category_selector"] = category_selector

        # --- Layout
        layout = backend.grid_lyt_t()
        if title_lyt is None:
            first_available_row = 0
        else:
            layout.addLayout(title_lyt, 0, 0, 1, 1)
            first_available_row = 1
        layout.addWidget(category_selector, first_available_row, 0, 1, 1)
        layout.addLayout(advanced_mode_lyt, first_available_row + 1, 0, 1, 1)
        layout.addLayout(button_lyt, first_available_row + 2, 0, 1, 1)
        output.library_wgt.setLayout(layout)

        return output

    def ReassignCloseButtonTarget(self) -> None:
        """"""
        current = self.library_wgt
        main_window = None
        while current is not None:
            main_window = current
            current = current.parent()

        self._widget["close"].SetFunction(main_window.close)

    def ToggleAdvancedMode(self, advanced_mode: bool, /) -> None:
        """"""
        for s_name, section in self.functional.items():
            if section.ppt.basic:
                should_check_parameters = True
            elif advanced_mode:
                section.interface.library_wgt.setVisible(True)
                should_check_parameters = True
            else:
                section.interface.library_wgt.setVisible(False)
                should_check_parameters = False

            if should_check_parameters:
                for _, parameter in section.active_parameters:
                    if not parameter.ppt.basic:
                        if advanced_mode:
                            parameter.interface.SetVisible(True)
                        else:
                            parameter.interface.SetVisible(False)

    def SyncWithFunctional(self) -> None:
        """"""
        config_typed = self.functional.active_as_typed_dict

        for s_name, section in self.functional.items():
            section_typed = config_typed[s_name]

            for p_name, parameter in section.prm_iterator:
                interface = parameter.interface
                if p_name in section_typed:
                    value = section_typed[p_name]
                    if not isinstance(value, invalid_t | unset_t):
                        interface.value.Assign(value, parameter.hint)
                        unit = parameter.unit_name
                        if unit is not None:
                            interface.unit.setText(unit)
                elif parameter.ppt.optional:
                    interface.value.Assign(parameter.default, parameter.hint)

    def UpdateFromNewDict(self, issues: h.Sequence[str], /) -> None:
        """"""
        if issues.__len__() > 0:
            self.backend.ShowErrorMessage("\n".join(issues), parent=self.library_wgt)
            return

        category_selector = self._widget["category_selector"]
        if isinstance(category_selector, self.backend.tabs_t):
            # Note: idx^th layout: category_selector.widget(t_idx).widget().layout().
            while category_selector.count() > 0:
                category_selector.removeTab(0)
        else:
            layout = category_selector.widget().layout()
            while layout.count() > 0:
                layout.itemAt(0).widget().setParent(None)

        # TODO: Why is it necessary to call SectionsAndCategories again? Actually, the
        #     problem could be more general: How to handle parameters present in the new
        #     dict/INI file that were not present in the previous/initial INI file?
        _ = SectionsAndCategories(self.functional, category_selector, self.backend)
        self.SyncWithFunctional()
        self.ToggleAdvancedMode(self._widget["adv_mode"].true_btn.isChecked())

        path_ini = self.functional.path
        self._widget["path_ini"].Assign(path_ini, None)
        self._widget["history_button"].setEnabled(True)
        if str(path_ini) not in (
            _elm.text() for _elm in self._widget["history_menu"].actions()
        ):
            self._widget["history_menu"].addAction(str(path_ini))

        if self.UpdateHistory is not None:
            self.UpdateHistory(path_ini)

    def LaunchAction(self) -> None:
        """"""
        self.setEnabled(False)
        self.backend.qt_core_app_t.processEvents()

        try:
            self.functional.SyncWithInterface()
            self.Action(self.functional.active_as_typed_dict)
        except Exception as exception:
            trace = nspt.trace()[-1]
            context = "\n".join(trace.code_context)
            self.backend.ShowErrorMessage(
                f"{trace.filename}@{trace.lineno}:{trace.function}\n"
                f"{context}\n"
                f"{exception}",
                parent=self.library_wgt,
            )

        self.setEnabled(True)

    def ShowInConsole(self) -> None:
        """"""
        as_str = []
        max_length = -1
        for s_name, section in self.active_as_str_dict.items():
            as_str.append(f"{FormattedName(s_name).upper()}")
            for p_name, parameter in section.items():
                formatted = FormattedName(p_name)
                as_str.append(f"    {formatted}:{parameter}")
                max_length = max(max_length, formatted.__len__() + 4)

        as_str = "\n".join(map(lambda _: _AlignSemiColon(_, max_length), as_str))

        L.info(f"CONFIGURATION\n{as_str}")

    def SaveConfig(self, new_ini: bool, /) -> None:
        """"""
        if new_ini:
            path_chooser = path_chooser_t.New("output", "document", message="Save Config As")
            path = path_chooser.NewSelected()
            if path is None:
                return

            self.functional.path = path
        elif self.functional.path is None:
            return

        issues = SaveConfigToINIDocument(self.active_as_str_dict, self.functional.path)
        if issues.__len__() > 0:
            self.backend.ShowErrorMessage("\n".join(issues), parent=self)

    def __getattr__(self, attribute: str, /) -> h.Any:
        """
        E.g., used for "show".
        """
        try:
            output = object.__getattribute__(self, attribute)
        except AttributeError:
            output = getattr(self.library_wgt, attribute)

        return output


def _AlignSemiColon(string: str, max_length: int, /) -> str:
    """"""
    if ":" not in string:
        return string

    name, value = string.split(":")
    return f"{name}: {(max_length - name.__len__()) * ' '}{value}"


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
