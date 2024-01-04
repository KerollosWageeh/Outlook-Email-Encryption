from PyQt5.QtWidgets import QFrame, QScrollArea, QWidget, QToolBar, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox, QSizePolicy, QFileDialog ,QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from outlook import OutlookHandler
from encryption import EncryptionHandler
import base64
class ComposeEmail(QMainWindow):
    def __init__(self):
        super().__init__()
        self.attachments = []
        self.setWindowTitle("Compose Secure Email")
        self.setWindowIcon(QIcon("icons/new_email.png"))
        self.setWindowState(Qt.WindowMaximized)
        self.setFixedSize(800, 500)
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setIconSize(QSize(32, 32))

        new_attachment_action = toolbar.addAction("Attach a new file")
        new_attachment_action.triggered.connect(self.attach_file)
        new_attachment_action.setStatusTip("Attach a new file")
        new_attachment_icon = QIcon("icons/new_attachment.png")
        new_attachment_action.setIcon(new_attachment_icon)
        toolbar.addSeparator()

        # send_email_action = toolbar.addAction("Send Email")
        # send_email_action.triggered.connect(self.send)
        # send_email_action.setStatusTip("Send Email")
        # send_email_icon = QIcon("icons/send_email.png")
        # send_email_action.setIcon(send_email_icon)

        self.addToolBar(toolbar)

        central_widget = QWidget(self)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(central_widget)
        # VBox layout takes the window width
        main_layout = QHBoxLayout(central_widget) # Assign layout to central_widget
        form_layout = QFormLayout()
        form_layout.setContentsMargins(50, 50, 50, 50)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_attachments_names = QWidget(scroll_area)
        scroll_area.setWidget(scroll_attachments_names)
        self.attachments_layout = QVBoxLayout(scroll_attachments_names)
        self.attachments_layout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.attachments_layout.setAlignment(Qt.AlignTop)
        self.attachments_layout.addWidget(QLabel("Attachments:"))
        scroll_attachments_names.setLayout(self.attachments_layout)
        main_layout.addWidget(scroll_area, 1)

        horizontal_separator = QFrame(central_widget)
        horizontal_separator.setFrameShape(QFrame.VLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(horizontal_separator, 1)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)

        self.to_line_edit = QLineEdit(form_widget)
        self.to_line_edit.setPlaceholderText("Enter recipient's email address")
        self.to_line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.subject_line_edit = QLineEdit()
        self.subject_line_edit.setPlaceholderText("Enter subject")
        self.message_text_edit = QTextEdit()
        self.message_text_edit.setPlaceholderText("Enter message")
        form_layout.addRow("To:", self.to_line_edit)
        form_layout.addRow("Subject:", self.subject_line_edit)
        form_layout.addRow("Message:", self.message_text_edit)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)

        form_layout.addRow(self.send_button)
        main_layout.addWidget(form_widget, 4) # Add form_layout to main_layout
        self.show()



    def send(self):
        to = self.to_line_edit.text()
        subject = self.subject_line_edit.text()
        message = self.message_text_edit.toPlainText()
        try:
            encrypted_message = EncryptionHandler.ecryptMail(to, subject, message, self.attachments)
        except Exception as e:
            QMessageBox.critical(self, "Recipient Not Found", f"Recipient {to} not registered in the secure email system.")
            return


        try:
            OutlookHandler.send_email(to, base64.b64encode(encrypted_message).decode('utf-8'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: Please make sure your windows Outlook client is running.")
            return

        QMessageBox.information(self, "Message sent", f"Message sent to {to} with subject {subject}")
        self.close()



    def attach_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*);;Text Files (*.txt)",
        options=options)

        if file_name:
            QMessageBox.information(self, "File Attached", f"File '{file_name.split('/')[-1]}' attached successfully.")
            attachement_label = QLabel(file_name.split('/')[-1])
            attachement_label.setWordWrap(True)
            self.attachments_layout.addWidget(attachement_label)
            self.attachments.append(file_name)