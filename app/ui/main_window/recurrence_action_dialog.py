from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class RecurrenceActionDialog(QDialog):
    """
    Tekrarlayan görev için eylem seçim diyalogu.

    Kullanım:
        dlg = RecurrenceActionDialog("edit", task.title, parent=self)
        result = dlg.exec()
        if result == RecurrenceActionDialog.ONLY_THIS:
            ...
        elif result == RecurrenceActionDialog.ALL_SERIES:
            ...
    """

    ONLY_THIS  = 1
    ALL_SERIES = 2

    _LABELS = {
        "edit": {
            "title":      "Tekrarlayan Görevi Düzenle",
            "only_this":  "Sadece bunu düzenle",
            "all_series": "Tüm seriyi düzenle",
        },
        "delete": {
            "title":      "Tekrarlayan Görevi Sil",
            "only_this":  "Sadece bunu sil",
            "all_series": "Tüm seriyi sil",
        },
    }

    def __init__(self, action: str, task_title: str, parent=None):
        super().__init__(parent)
        labels = self._LABELS[action]
        self.setWindowTitle(labels["title"])
        self.setModal(True)
        self.setMinimumWidth(380)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        lbl = QLabel(f'"{task_title}" tekrarlayan bir görev.')
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_only = QPushButton(labels["only_this"])
        btn_only.clicked.connect(lambda: self.done(self.ONLY_THIS))

        btn_all = QPushButton(labels["all_series"])
        if action == "delete":
            btn_all.setObjectName("btn_danger")
        btn_all.clicked.connect(lambda: self.done(self.ALL_SERIES))

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_only)
        btn_row.addWidget(btn_all)
        root.addLayout(btn_row)
