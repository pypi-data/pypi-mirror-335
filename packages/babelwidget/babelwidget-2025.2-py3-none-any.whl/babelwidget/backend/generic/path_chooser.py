"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

"""
valid_types: {"Type": "extension", "Type": ("extension", "extension",...), ...}
filter: "Image files (*.png *.xpm *.jpg);Text files (*.txt);Any files (*)"
"""

import typing as h
from pathlib import Path as path_t

import PyQt6.QtGui as qtui
import PyQt6.QtWidgets as wdgt

path_chooser_h = h.TypeVar("path_chooser_h")

key_e = qtui.QKeySequence.StandardKey
color_e = qtui.QColorConstants

_WHY = {"input": "Reading/Input", "output": "Writing/Output"}
_WHAT = {
    "document": "a Document",
    "folder": "a Folder",
    "any": "a Document or a Folder",
}

_N_COLUMNS = 6
_N_COLUMNS_OVER_3 = _N_COLUMNS // 3


class path_chooser_t(wdgt.QDialog):
    folder: path_t | None
    purpose: h.Literal["input", "output"]
    kind: h.Literal["any", "document", "folder"]
    accepts_documents: bool
    accepts_folders: bool
    should_show_hidden: bool

    documents: list[path_t] | None
    folders: list[path_t] | None
    others: list[path_t] | None

    parents: tuple[path_t, ...] | None
    parents_wgt: wdgt.QComboBox
    goto_parent_wgt: wdgt.QPushButton
    nodes: list[path_t] | None
    nodes_wgt: wdgt.QListWidget
    hidden_label: wdgt.QLabel
    hidden_true: wdgt.QRadioButton
    hidden_false: wdgt.QRadioButton
    extensions_wgt: wdgt.QComboBox
    custom: wdgt.QLineEdit | None
    create: wdgt.QPushButton | None
    cancel: wdgt.QPushButton
    enter: wdgt.QPushButton
    select: wdgt.QPushButton

    selected_node: path_t | None

    _programmatically_caused: bool

    @classmethod
    def New(
        cls,
        purpose: h.Literal["input", "output"],
        kind: h.Literal["any", "document", "folder"],
        /,
        *,
        folder: str | path_t = path_t.home(),
        message: str | None = None,
    ) -> h.Self:
        """"""
        output = cls()

        output.folder = None
        output.purpose = purpose
        output.kind = kind
        output.accepts_documents = kind in ("document", "any")
        output.accepts_folders = kind in ("folder", "any")
        output.should_show_hidden = False
        output.documents = None
        output.folders = None
        output.others = None
        output.selected_node = None
        output._programmatically_caused = False

        if message is None:
            message = ""
        else:
            message += ": "
        title_wgt = wdgt.QLabel(
            f"<h3>{message}Select {_WHAT[kind]} for {_WHY[purpose]}</h3>"
        )

        parents_wgt = wdgt.QComboBox()
        goto_parent_wgt = wdgt.QPushButton("Up")

        nodes_wgt = wdgt.QListWidget()

        hidden_label = wdgt.QLabel("Show Hidden")
        hidden_true = wdgt.QRadioButton("True")
        hidden_false = wdgt.QRadioButton("False")
        if output.accepts_documents:
            extensions_wgt = wdgt.QComboBox()
        else:
            extensions_wgt = None

        if purpose == "output":
            custom = wdgt.QLineEdit()
            create = wdgt.QPushButton("Create Folder")
        else:
            custom = create = None

        cancel = wdgt.QPushButton("Cancel")
        enter = wdgt.QPushButton("Enter Folder")
        select = wdgt.QPushButton("Select")

        output.parents = None
        output.parents_wgt = parents_wgt
        output.goto_parent_wgt = goto_parent_wgt
        output.nodes = None
        output.nodes_wgt = nodes_wgt
        output.hidden_label = hidden_label
        output.hidden_true = hidden_true
        output.hidden_false = hidden_false
        output.extensions_wgt = extensions_wgt
        output.custom = custom
        output.create = create
        output.cancel = cancel
        output.enter = enter
        output.select = select

        hidden_true.setChecked(False)
        hidden_false.setChecked(True)
        if create is not None:
            create.setEnabled(False)
        enter.setEnabled(False)
        select.setEnabled(output.accepts_folders)

        # cancel.setStyleSheet('QPushButton {background-color: red;}')
        # enter.setStyleSheet('QPushButton {background-color: blue;}')
        # select.setStyleSheet('QPushButton {background-color: green;}')

        output.SetFolder(path_t(folder))

        parents_wgt.currentIndexChanged.connect(output._OnFolderUpChangeRequest)
        goto_parent_wgt.clicked.connect(lambda: output._OnFolderUpChangeRequest(1))
        nodes_wgt.currentRowChanged.connect(output._OnNewNodeSelection)
        nodes_wgt.itemDoubleClicked.connect(output._OnNodeDoubleClicked)
        if custom is not None:
            custom.textChanged.connect(output._OnCustomChanged)
            create.clicked.connect(output._OnFolderCreationRequest)
        hidden_true.released.connect(output._OnHiddenChangeRequest)
        hidden_false.released.connect(output._OnHiddenChangeRequest)
        if extensions_wgt is not None:
            extensions_wgt.currentIndexChanged.connect(
                output._OnExtensionFilteringRequest
            )
        cancel.clicked.connect(output.close)
        enter.clicked.connect(output._OnFolderDownChangeRequest)
        select.clicked.connect(output._OnNodeSelection)

        # For some reason, clearSelection leaves a dimmed selection instead of
        # "removing" it completely. Using setCurrentRow(-1) instead.
        shortcut = qtui.QShortcut(key_e.Deselect, output)
        shortcut.activated.connect(lambda: output.nodes_wgt.setCurrentRow(-1))

        layout = wdgt.QGridLayout()
        layout.addWidget(title_wgt, 0, 0, 1, _N_COLUMNS)
        layout.addWidget(parents_wgt, 1, 0, 1, _N_COLUMNS - 1)
        layout.addWidget(goto_parent_wgt, 1, _N_COLUMNS - 1)
        layout.addWidget(nodes_wgt, 2, 0, 1, _N_COLUMNS)
        layout.addWidget(hidden_label, 3, 0)
        layout.addWidget(hidden_true, 3, 1)
        layout.addWidget(hidden_false, 3, 2)
        if extensions_wgt is not None:
            layout.addWidget(extensions_wgt, 3, 3, 1, 3)
        if custom is None:
            next_row = 4
        else:
            layout.addWidget(custom, 4, 0, 1, _N_COLUMNS - 1)
            layout.addWidget(create, 4, _N_COLUMNS - 1)
            next_row = 5
        layout.addWidget(cancel, next_row, 0, 1, _N_COLUMNS_OVER_3)
        layout.addWidget(enter, next_row, _N_COLUMNS_OVER_3, 1, _N_COLUMNS_OVER_3)
        layout.addWidget(select, next_row, 2 * _N_COLUMNS_OVER_3, 1, _N_COLUMNS_OVER_3)
        output.setLayout(layout)

        return output

    def NewSelected(self) -> path_t | None:
        """"""
        self.exec()
        return self.selected_node

    def SetFolder(self, folder: path_t, /) -> None:
        """"""
        nodes = tuple(folder.glob("*"))
        documents = sorted(filter(path_t.is_file, nodes))
        folders = sorted(filter(_NodeIsFolderLike, nodes))
        others = sorted(set(nodes).difference(documents + folders))

        self.folder = folder
        self.parents = (folder,) + tuple(folder.parents)

        self.documents = documents
        self.folders = folders
        self.others = others

        self.parents_wgt.clear()
        self.parents_wgt.addItems(map(str, self.parents))

        self._UpdateNodes()

        if self.extensions_wgt is not None:
            # /!\\ Currently, the extension of hidden documents are discarded.
            extensions = ("*",) + tuple(
                set(
                    filter(
                        lambda _: _.__len__() > 0,
                        (
                            _.suffix
                            for _ in documents
                            if not str(_.name).startswith(".")
                        ),
                    )
                )
            )
            self.extensions_wgt.clear()
            self.extensions_wgt.addItems(extensions)

    def _UpdateNodes(self) -> None:
        """"""
        MatchHiddenStatus = lambda _: self.should_show_hidden or not str(
            _.name
        ).startswith(".")
        if self.extensions_wgt is None:
            valid_extension = "*"
        else:
            valid_extension = self.extensions_wgt.currentText()
        documents = sorted(
            filter(
                lambda _: MatchHiddenStatus(_) and (valid_extension in ("*", _.suffix)),
                self.documents,
            )
        )
        folders = sorted(filter(MatchHiddenStatus, self.folders))
        others = sorted(filter(MatchHiddenStatus, self.others))

        documents_postfixes = ("",) * documents.__len__()
        folders_postfixes = ("/",) * folders.__len__()
        others_postfixes = ("?",) * others.__len__()

        documents_validity_s = (self.accepts_documents,) * documents.__len__()
        folders_validity_s = (self.accepts_folders,) * folders.__len__()
        others_validity_s = (False,) * others.__len__()
        if self.accepts_folders:
            nodes = folders + documents + others
            postfixes = folders_postfixes + documents_postfixes + others_postfixes
            validity_s = folders_validity_s + documents_validity_s + others_validity_s
        else:
            nodes = documents + folders + others
            postfixes = documents_postfixes + folders_postfixes + others_postfixes
            validity_s = documents_validity_s + folders_validity_s + others_validity_s

        self.nodes = nodes
        self.nodes_wgt.clear()
        self.nodes_wgt.addItems(f"{_.name}{__}" for _, __ in zip(nodes, postfixes))

        for row, valid in enumerate(validity_s):
            if not valid:
                self.nodes_wgt.item(row).setForeground(color_e.Gray)

    def _OnFolderUpChangeRequest(self, index: int, /) -> None:
        """"""
        if self._programmatically_caused:
            return

        self._programmatically_caused = True
        self.SetFolder(self.parents[index])
        self._programmatically_caused = False

    def _OnFolderDownChangeRequest(self) -> None:
        """"""
        if self._programmatically_caused:
            return

        self._programmatically_caused = True
        self.SetFolder(self.nodes[self.nodes_wgt.currentRow()])
        self._programmatically_caused = False

    def _OnNewNodeSelection(self, row: int, /) -> None:
        """"""
        if row < 0:
            self.enter.setEnabled(False)
            self.select.setEnabled(self.accepts_folders)
        else:
            node = self.nodes[row]
            node_is_folder = _NodeIsFolderLike(node)
            self.enter.setEnabled(node_is_folder)
            self.select.setEnabled(
                (self.accepts_documents and node.is_file())
                or (self.accepts_folders and node_is_folder)
            )

    def _OnNodeDoubleClicked(self, _: wdgt.QListWidgetItem, /) -> None:
        """"""
        if self._programmatically_caused:
            return

        node = self.nodes[self.nodes_wgt.currentRow()]
        if node.is_file():
            if self.accepts_documents:
                if self.purpose == "input":
                    if _NodeIsEmpty(node):
                        confirmed = _ConfirmedAnswer(
                            f"{node} is empty.", "Do you want to open/use it anyway?"
                        )
                    else:
                        confirmed = True
                else:
                    confirmed = _ConfirmedAnswer(
                        f"{node} exists.", "Do you want to override it?"
                    )
                if confirmed:
                    self.selected_node = node
                    self.close()
            elif self.custom is not None:
                self.custom.setText(node.name)
        elif _NodeIsFolderLike(node):
            self._programmatically_caused = True
            self.SetFolder(node)
            self._programmatically_caused = False

    def _OnHiddenChangeRequest(self) -> None:
        """"""
        self.should_show_hidden = self.hidden_true.isChecked()
        self.hidden_false.setChecked(not self.should_show_hidden)

        self._programmatically_caused = True
        self._UpdateNodes()
        self._programmatically_caused = False

    def _OnExtensionFilteringRequest(self) -> None:
        """"""
        if self._programmatically_caused:
            return

        self._programmatically_caused = True
        self._UpdateNodes()
        self._programmatically_caused = False

    def _OnCustomChanged(self, content: str, /) -> None:
        """"""
        self.create.setEnabled(not (self.folder / content).exists())

    def _OnFolderCreationRequest(self) -> None:
        """"""
        folder = self.folder / self.custom.text()
        try:
            folder.mkdir()
        except Exception as exception:
            dialog = wdgt.QMessageBox()
            dialog.setText(f"Folder {folder} could not be created:\n{exception}")
            _ = dialog.exec()
        else:
            self._programmatically_caused = True
            self.SetFolder(folder)
            self._programmatically_caused = False

    def _OnNodeSelection(self) -> None:
        """"""
        if self.custom is None:
            custom = ""
        else:
            custom = self.custom.text()
        if custom.__len__() > 0:
            node = self.folder / custom
        elif (row := self.nodes_wgt.currentRow()) >= 0:
            node = self.nodes[row]
        else:
            node = self.folder

        confirmed = False
        if self.purpose == "input":
            if self.accepts_documents and node.is_file():
                if _NodeIsEmpty(node):
                    confirmed = _ConfirmedAnswer(
                        f"{node} is empty.", "Do you want to open/use it anyway?"
                    )
                else:
                    confirmed = True
            elif self.accepts_folders and _NodeIsFolderLike(node):
                if _NodeIsEmpty(node):
                    confirmed = _ConfirmedAnswer(
                        f"{node} is empty.", "Do you want to use it as input anyway?"
                    )
                else:
                    confirmed = True
        else:
            if self.accepts_documents and node.is_file():
                confirmed = _ConfirmedAnswer(
                    f"{node} exists.", "Do you want to override it?"
                )
            elif self.accepts_folders and _NodeIsFolderLike(node):
                if _NodeIsEmpty(node):
                    confirmed = True
                else:
                    confirmed = _ConfirmedAnswer(
                        f"{node} is not empty.",
                        "Do you want to use it as output anyway?",
                    )

        if confirmed:
            self.selected_node = node
            self.close()


def _NodeIsFolderLike(node: path_t, /) -> bool:
    """"""
    return node.is_dir() or node.is_junction() or node.is_mount()


def _NodeIsEmpty(node: path_t, /) -> bool:
    """"""
    if node.is_file():
        return node.stat().st_size == 0

    return tuple(node.glob("*")).__len__() == 0


def _ConfirmedAnswer(message: str, question: str, /) -> bool:
    """"""
    dialog = wdgt.QMessageBox()

    dialog.setText(message)
    dialog.setInformativeText(question)
    dialog.setStandardButtons(
        wdgt.QMessageBox.StandardButton.Yes | wdgt.QMessageBox.StandardButton.No
    )
    dialog.setDefaultButton(wdgt.QMessageBox.StandardButton.No)

    answer = dialog.exec()

    return answer == wdgt.QMessageBox.StandardButton.Yes


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
