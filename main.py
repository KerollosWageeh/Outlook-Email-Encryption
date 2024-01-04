from PyQt5.QtWidgets import QDesktopWidget, QApplication, QLabel, QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from new_mail import ComposeEmail
from outlook import OutlookHandler
from decryption import DecryptionHandler
from encryption import EncryptionHandler
import os
import sys

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("Secure Email Client Group 7")
        self.setWindowIcon(QIcon("icons/secure_email.png"))
        self.setWindowState(Qt.WindowMaximized)
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Quit", self.close)

        edit_menu = menu_bar.addMenu("&Edit")
        # edit_menu.addAction("Undo", self.undo)
        # edit_menu.addAction("Redo", self.redo)

        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)

        # Add an empty spacer to the left side of the toolbar
        spacer_widget = QWidget()
        spacer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer_widget)

        # Compose button
        compose_action = toolbar.addAction("Compose")
        compose_action.triggered.connect(self.new_email)
        compose_action.setStatusTip("Create a new secure email")
        compose_action.setShortcut("Ctrl+N")
        compose_icon = QIcon("icons/new_email.png")
        compose_action.setIcon(compose_icon)

        # Refresh Inbox button
        refresh_action = toolbar.addAction("Refresh")
        refresh_action.triggered.connect(self.fetch_emails)
        refresh_action.setStatusTip("Refresh")
        refresh_icon = QIcon("icons/refresh.png")  # Replace with the actual refresh icon
        refresh_action.setIcon(refresh_icon)

        status_bar = self.statusBar()
        status_bar.showMessage("Application loaded", 3000)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_horizontal_layout = QHBoxLayout(central_widget)

        self.incoming_emails_widget = QVBoxLayout()
        self.incoming_emails_widget.setAlignment(Qt.AlignTop)

        main_horizontal_layout.addLayout(self.incoming_emails_widget, 1)

        horizontal_separator = QFrame(central_widget)
        horizontal_separator.setFrameShape(QFrame.VLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)
        main_horizontal_layout.addWidget(horizontal_separator, 1)
        self.view_email_widget = QVBoxLayout()
        self.view_email_widget.setAlignment(Qt.AlignTop)
        main_horizontal_layout.addLayout(self.view_email_widget, 3)
        self.fetch_emails()

    def center_window(self, window):
        screen_geometry = QDesktopWidget().screenGeometry()
        x = (screen_geometry.width() - window.width()) // 2
        y = (screen_geometry.height() - window.height()) // 2
        window.move(x, y)

    def close(self):
        self.app.quit()

    def new_email(self):
        self.compose_email_widget = ComposeEmail()
        self.center_window(self.compose_email_widget)
        self.compose_email_widget.show()
    def fetch_emails(self):
        emails = OutlookHandler.get_inbox()

        # Clear the existing layout
        while self.incoming_emails_widget.count():
            item = self.incoming_emails_widget.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        for email in emails:
            email_card = QVBoxLayout()
            email_card.setAlignment(Qt.AlignTop)
            email_card.addWidget(QLabel(f"From: {email.SenderName}"))
            row = QHBoxLayout()
            row.addWidget(QLabel(f"On: {email.ReceivedTime.strftime('%d/%m/%Y %H:%M:%S')}"))
            row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            view_button = QPushButton("View")
            view_button.setProperty("email", email)
            view_button.clicked.connect(self.view_email_pressed)
            row.addWidget(view_button)
            email_card.addLayout(row)
            self.incoming_emails_widget.addLayout(email_card)

        horizontal_separator = QFrame()
        horizontal_separator.setFrameShape(QFrame.HLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)
        self.incoming_emails_widget.addWidget(horizontal_separator)

    def view_email_pressed(self):
        email = self.sender().property("email")
        print(email)
        message = DecryptionHandler.decrypt(email.Sender.GetExchangeUser().PrimarySmtpAddress, email.Body)

        # Clear the existing layout
        while self.view_email_widget.count():
            item = self.view_email_widget.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)


        from_row = QHBoxLayout()
        from_word_label = QLabel("From:")
        from_word_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff;border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        from_row.addWidget(from_word_label)

        from_label = QLabel(email.SenderName)
        from_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff;border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        from_row.addWidget(from_label)


        on_word_label = QLabel("Date and Time:")
        on_word_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        from_row.addWidget(on_word_label)

        on_label = QLabel(email.ReceivedTime.strftime('%d/%m/%Y %H:%M:%S'))
        on_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        from_row.addWidget(on_label)
        from_row.setStretch(0,0)
        from_row.setStretch(1,3)
        from_row.setStretch(2,0)
        from_row.setStretch(3,1)
        self.view_email_widget.addLayout(from_row)

        subject_row = QHBoxLayout()

        subject_word_label = QLabel("Subject:")
        subject_word_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color:#ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        subject_row.addWidget(subject_word_label)

        subject_label = QLabel(message['subject'])
        subject_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        subject_row.addWidget(subject_label)
        subject_row.setStretch(0, 0)
        subject_row.setStretch(1,1)
        self.view_email_widget.addLayout(subject_row)

        if(len(message['attachments_names']) > 0):
            attachments_word_label = QLabel("Attachments:")
            attachments_word_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000; padding: 5px;")
            self.view_email_widget.addWidget(attachments_word_label)
            for attachment in message['attachments_names']:
                attachment_row = QHBoxLayout()
                attachment_label = QLabel(attachment)
                attachment_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
                attachment_row.addWidget(attachment_label)
                attachment_row.setStretch(0, 1)
                download_button = QPushButton("Download")
                download_button.setProperty("attachment", attachment)
                download_button.setProperty("attachments_data", message['attachments_data'])
                download_button.clicked.connect(self.download_attachment_pressed)
                attachment_row.addWidget(download_button)
                self.view_email_widget.addLayout(attachment_row)
                self.view_email_widget.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum))

        subject_word_label = QLabel("Message:")
        subject_word_label.setStyleSheet("font-size: 14px; color: #000000; padding: 5px;")
        self.view_email_widget.addWidget(subject_word_label)

        content = message['message'].replace("\n", "<br>")
        content_label = QLabel(content)
        content_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; background-color: #ffffff; border: 1px solid #000000; padding: 5px; border-radius: 5px; margin: 5px;")
        self.view_email_widget.addWidget(content_label)

        

    def download_attachment_pressed(self):
        attachment = self.sender().property("attachment")
        attachments_data = self.sender().property("attachments_data")

        if not os.path.exists("SecureEmailDownloads"):
            os.mkdir("SecureEmailDownloads")


        with open("SecureEmailDownloads/"+attachment, 'wb') as file:
            file.write(attachments_data[attachment])

        status_bar = self.statusBar()
        status_bar.showMessage(f"Attachment {attachment} downloaded successfully", 3000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mail_interface = MainWindow(app)


    mail_interface.show()
    EncryptionHandler.initApp()
    sys.exit(app.exec_())
