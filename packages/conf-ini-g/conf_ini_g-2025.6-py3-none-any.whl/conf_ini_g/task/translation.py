"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

from babelwidget.api.widget import base_h as library_wgt_h
from conf_ini_g.catalog.choices import choices_wgt_t
from conf_ini_g.catalog.collection import collection_wgt_t
from conf_ini_g.catalog.none import none_wgt_t
from conf_ini_g.catalog.text_line import text_line_t
from conf_ini_g.constant.translator import TYPE_WIDGET_TRANSLATOR
from value_factory.api.type import hint_t


def RegisterNewTranslation(new_type: type, widget_type: type[library_wgt_h], /) -> None:
    """"""
    if new_type in TYPE_WIDGET_TRANSLATOR:
        # Raising an exception is adapted here since it is a developer-oriented function
        raise ValueError(
            f"{new_type.__name__}: Type already registered with "
            f'"{TYPE_WIDGET_TRANSLATOR[new_type]}" in type-to-widget translations.'
        )

    TYPE_WIDGET_TRANSLATOR[new_type] = widget_type


def ValueWidgetTypeForType(hint: hint_t, /) -> type[library_wgt_h]:
    """"""
    if hint.only_matches_none:
        return none_wgt_t

    # First, look for annotations.
    if (nnts := hint.annotations) is not None:
        # First, look for an exact match.
        for annotation in nnts:
            stripe = type(annotation)
            if (output := TYPE_WIDGET_TRANSLATOR.get(stripe)) is not None:
                return output

        # Then, look for subclasses.
        for annotation in nnts:
            stripe = type(annotation)
            for registered, widget_type in TYPE_WIDGET_TRANSLATOR.items():
                if issubclass(stripe, registered):
                    return widget_type

    if hint.is_universal:
        return text_line_t
    if hint.is_literal:
        return choices_wgt_t
    if hint.is_sequence:
        return collection_wgt_t
    if hint.is_mapping:
        return text_line_t

    assert not hint.is_union

    # Then, look for types.
    stripe = hint.type

    # First, look for an exact match.
    if (output := TYPE_WIDGET_TRANSLATOR.get(stripe)) is not None:
        return output

    # Then, look for subclasses.
    for registered, widget_type in TYPE_WIDGET_TRANSLATOR.items():
        if issubclass(stripe, registered):
            return widget_type

    return text_line_t


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
