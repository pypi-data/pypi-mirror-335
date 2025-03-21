"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import importlib.util as mprt
import sys as sstm
import types as t
from os import sep as PATH_SEPARATOR
from pathlib import Path as path_t

from babelwidget.type.protocol import backend_p


@d.dataclass(repr=False, eq=False)
class backend_t(backend_p):
    name: str

    def __post_init__(self) -> None:
        """"""
        base_path = path_t(__file__).parent
        package_path = base_path.parent
        path = base_path / "backend" / self.name
        if not path.is_dir():
            raise ValueError(f"Invalid backend folder: {path}.")

        standard_modules = set(sstm.stdlib_module_names).union(
            sstm.builtin_module_names
        )
        for node in path.rglob("*.py"):
            if not node.is_file():
                continue

            relative = node.relative_to(package_path)
            name = str(relative.parent / relative.stem).replace(PATH_SEPARATOR, ".")
            spec = mprt.spec_from_file_location(name, node)
            module = mprt.module_from_spec(spec)
            sstm.modules[name] = module
            spec.loader.exec_module(module)

            for name in dir(module):
                if name[0] == "_":
                    continue

                element = getattr(module, name)
                if not (
                    isinstance(element, t.ModuleType)
                    or (not hasattr(element, "__module__"))
                    or (element.__module__[0] == "_")
                    or (element.__module__ in standard_modules)
                ):
                    setattr(self, name, element)


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
