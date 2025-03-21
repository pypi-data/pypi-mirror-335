"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d


@d.dataclass(slots=True, repr=False, eq=False)
class ppt_t:
    """
    basic: As opposed to "advanced" or "expert".
    optional: Set by __post_init__ when used for a parameter.

    For sections only:
        - growable
        - category
    """

    short: str = "No Short Description Provided"
    long: str = "No Long Description Provided"
    basic: bool = True
    optional: bool = False
    #
    growable: bool | None = None
    category: str = "No Category Provided"

    def __post_init__(self) -> None:
        """"""
        assert isinstance(self.short, str)
        assert isinstance(self.long, str)
        assert isinstance(self.basic, bool)
        assert isinstance(self.optional, bool)
        assert isinstance(self.growable, bool | None)
        assert isinstance(self.category, str | None)

        # The condition "self.basic or self.optional" cannot be tested here since:
        # - it is not known whether the property if for a section or parameter,
        # - if for a parameter, self.optional is set by prm_t.__post_init__.
        # Hence, this condition is tested separately in section and parameter Issues.

    def __str__(self) -> str:
        """"""
        if self.growable is None:
            is_growable_title = is_growable_value = ""
        else:
            is_growable_title = "/Growable"
            is_growable_value = f"/{self.growable}"

        if self.category is None:
            category = ""
        else:
            category = f"\nCategory: {self.category}"

        return (
            f"Short: {self.short}\n"
            f"Long:  {self.long}\n"
            f"Basic/Optional{is_growable_title}: "
            f"{self.basic}/{self.optional}{is_growable_value}"
            f"{category}"
        )

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
