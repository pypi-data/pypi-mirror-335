"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from babelwidget.api.backend import backend_t
from babelwidget.api.widget import dropdown_choice_h as dropdown_choice_wgt_h
from conf_ini_g.interface.window.parameter.value import value_wgt_a
from value_factory.api.catalog import choices_t
from value_factory.api.type import hint_t


@d.dataclass(repr=False, eq=False)
class choices_wgt_t(value_wgt_a):
    library_wgt: dropdown_choice_wgt_h

    @classmethod
    def New(
        cls,
        stripe: hint_t | None,
        backend: backend_t,
        /,
    ) -> h.Self:
        """
        stripe: None means that the choices will be dynamically set.
        """
        if isinstance(stripe, hint_t):
            if stripe.is_literal:
                options_as_str = stripe.literal_s
            else:
                annotation = stripe.FirstAnnotationWithType(choices_t)
                options_as_str = annotation.options_as_str
        else:
            options_as_str = ("No choices yet",)

        library_wgt = backend.dropdown_choice_t()
        output = cls(
            library_wgt, "currentIndexChanged", backend, library_wgt=library_wgt
        )

        for choice in map(str, options_as_str):
            output.library_wgt.addItem(choice)

        return output

    def Assign(self, value: str, _: h.Any, /) -> None:
        """"""
        choices = tuple(map(self.itemText, range(self.count())))
        try:
            where = choices.index(value)
        except ValueError:
            choices = " or ".join(choices)
            raise ValueError(f"Invalid value: Actual={value}; Expected={choices}.")

        self.setCurrentIndex(where)

    def Text(self) -> str:
        """"""
        return self.library_wgt.currentText()

    def __getattr__(self, attribute: str, /) -> h.Any:
        """
        E.g., used for "SetFunction".
        """
        try:
            output = self.__getattribute__(attribute)
        except AttributeError:
            output = getattr(self.library_wgt, attribute)

        return output


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
