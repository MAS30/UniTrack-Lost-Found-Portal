import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


# ---------------- DATABASE SETUP ---------------- #

connection = sqlite3.connect("unitrack.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS found_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    item_name TEXT,
    category TEXT,
    location TEXT,
    description TEXT,
    status TEXT
)
""")

connection.commit()
connection.close()


# ---------------- ADD ITEM WINDOW ---------------- #

class AddItemWindow(QWidget):

    def __init__(self, dashboard):

        super().__init__()

        self.dashboard = dashboard

        self.setWindowTitle("Add Found Item")
        self.resize(700, 650)

        # TITLE
        title = QLabel("Add Found Item", self)
        title.move(220, 30)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))

        # ITEM NAME
        item_label = QLabel("Item Name", self)
        item_label.move(70, 120)

        self.item_input = QLineEdit(self)
        self.item_input.move(70, 150)
        self.item_input.resize(560, 50)

        # CATEGORY
        category_label = QLabel("Category", self)
        category_label.move(70, 230)

        self.category_input = QLineEdit(self)
        self.category_input.move(70, 260)
        self.category_input.resize(560, 50)

        # LOCATION
        location_label = QLabel("Found Location", self)
        location_label.move(70, 340)

        self.location_input = QLineEdit(self)
        self.location_input.move(70, 370)
        self.location_input.resize(560, 50)

        # DESCRIPTION
        desc_label = QLabel("Description", self)
        desc_label.move(70, 450)

        self.description_input = QTextEdit(self)
        self.description_input.move(70, 480)
        self.description_input.resize(560, 80)

        # SAVE BUTTON
        save_button = QPushButton("Save Item", self)
        save_button.move(250, 585)
        save_button.resize(200, 50)

        save_button.clicked.connect(self.save_item)

    # SAVE ITEM
    def save_item(self):

        item_name = self.item_input.text()
        category = self.category_input.text()
        location = self.location_input.text()
        description = self.description_input.toPlainText()

        if item_name == "":

            QMessageBox.warning(
                self,
                "Error",
                "Item name is required."
            )

            return

        connection = sqlite3.connect("unitrack.db")
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO found_items
        (item_name, category, location, description, status)

        VALUES (?, ?, ?, ?, ?)
        """, (
            item_name,
            category,
            location,
            description,
            "Unclaimed"
        ))

        connection.commit()
        connection.close()

        QMessageBox.information(
            self,
            "Success",
            "Item saved successfully!"
        )

        # UPDATE DASHBOARD
        self.dashboard.update_stats()

        # CLEAR FIELDS
        self.item_input.clear()
        self.category_input.clear()
        self.location_input.clear()
        self.description_input.clear()


# ---------------- SEARCH WINDOW ---------------- #

class SearchWindow(QWidget):

    def __init__(self, dashboard):

        super().__init__()

        self.dashboard = dashboard

        self.setWindowTitle("Search Items")
        self.resize(1200, 750)

        # TITLE
        title = QLabel("Search Found Items", self)
        title.move(420, 30)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))

        # SEARCH LABEL
        search_label = QLabel("Search Item Name", self)
        search_label.move(70, 110)

        # SEARCH INPUT
        self.search_input = QLineEdit(self)
        self.search_input.move(70, 145)
        self.search_input.resize(550, 50)

        # SEARCH BUTTON
        search_button = QPushButton("Search", self)
        search_button.move(660, 145)
        search_button.resize(180, 50)

        search_button.clicked.connect(self.search_items)

        # RETURN BUTTON
        return_button = QPushButton("Mark As Returned", self)
        return_button.move(880, 145)
        return_button.resize(220, 50)

        return_button.clicked.connect(self.mark_returned)

        # TABLE
        self.table = QTableWidget(self)
        self.table.move(70, 240)
        self.table.resize(1040, 430)

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Item Name",
            "Category",
            "Location",
            "Description",
            "Status"
        ])

        # AUTO STRETCH TABLE
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # LOAD ALL ACTIVE ITEMS INITIALLY
        self.load_all_items()

    # LOAD ALL ITEMS
    def load_all_items(self):

        connection = sqlite3.connect("unitrack.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT * FROM found_items
        WHERE status != 'Returned'
        """)

        results = cursor.fetchall()

        connection.close()

        self.display_results(results)

    # SEARCH ITEMS
    def search_items(self):

        search_text = self.search_input.text()

        connection = sqlite3.connect("unitrack.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT * FROM found_items
        WHERE item_name LIKE ?
        AND status != 'Returned'
        """, ('%' + search_text + '%',))

        results = cursor.fetchall()

        connection.close()

        self.display_results(results)

    # DISPLAY RESULTS
    def display_results(self, results):

        self.table.setRowCount(len(results))

        for row_index, row_data in enumerate(results):

            for column_index, data in enumerate(row_data):

                self.table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(str(data))
                )

    # MARK RETURNED
    def mark_returned(self):

        selected_row = self.table.currentRow()

        if selected_row == -1:

            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an item first."
            )

            return

        item_id = self.table.item(selected_row, 0).text()

        connection = sqlite3.connect("unitrack.db")
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE found_items
        SET status = 'Returned'
        WHERE id = ?
        """, (item_id,))

        connection.commit()
        connection.close()

        QMessageBox.information(
            self,
            "Success",
            "Item marked as Returned!"
        )

        # REFRESH TABLE
        self.load_all_items()

        # UPDATE DASHBOARD
        self.dashboard.update_stats()


# ---------------- DASHBOARD ---------------- #

class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("UniTrack Dashboard")
        self.resize(1300, 750)

        # SIDEBAR
        sidebar = QLabel(self)
        sidebar.move(0, 0)
        sidebar.resize(300, 750)

        sidebar.setStyleSheet("""
            background-color: #1e293b;
            border-top-right-radius: 25px;
            border-bottom-right-radius: 25px;
        """)

        # DASHBOARD TITLE
        title = QLabel("UniTrack Dashboard", self)
        title.move(450, 35)
        title.setFont(QFont("Segoe UI", 30, QFont.Bold))

        # BUTTON STYLE
        button_style = """
            QPushButton{
                background-color: #3b82f6;
                color: white;
                border-radius: 16px;
                font-size: 17px;
                font-weight: bold;
            }

            QPushButton:hover{
                background-color: #2563eb;
            }
        """

        # ADD ITEM BUTTON
        add_item_btn = QPushButton("Add Found Item", self)
        add_item_btn.move(40, 170)
        add_item_btn.resize(220, 60)
        add_item_btn.setStyleSheet(button_style)

        # SEARCH BUTTON
        search_btn = QPushButton("Search Items", self)
        search_btn.move(40, 270)
        search_btn.resize(220, 60)
        search_btn.setStyleSheet(button_style)

        # BUTTON EVENTS
        add_item_btn.clicked.connect(self.open_add_item)
        search_btn.clicked.connect(self.open_search_window)

        # TOTAL ITEMS CARD
        self.total_items = QLabel(self)
        self.total_items.move(380, 190)
        self.total_items.resize(300, 160)

        self.total_items.setAlignment(Qt.AlignCenter)

        self.total_items.setStyleSheet("""
            background-color: #3b82f6;
            color: white;
            border-radius: 25px;
            font-size: 28px;
            font-weight: bold;
        """)

        # RETURNED ITEMS CARD
        self.returned_items = QLabel(self)
        self.returned_items.move(760, 190)
        self.returned_items.resize(300, 160)

        self.returned_items.setAlignment(Qt.AlignCenter)

        self.returned_items.setStyleSheet("""
            background-color: #10b981;
            color: white;
            border-radius: 25px;
            font-size: 28px;
            font-weight: bold;
        """)

        # LOAD STATS
        self.update_stats()

    # UPDATE STATS
    def update_stats(self):

        connection = sqlite3.connect("unitrack.db")
        cursor = connection.cursor()

        # ACTIVE ITEMS
        cursor.execute("""
        SELECT COUNT(*) FROM found_items
        WHERE status != 'Returned'
        """)

        active_items = cursor.fetchone()[0]

        # RETURNED ITEMS
        cursor.execute("""
        SELECT COUNT(*) FROM found_items
        WHERE status = 'Returned'
        """)

        returned = cursor.fetchone()[0]

        connection.close()

        self.total_items.setText(
            f"Active Lost Items\n{active_items}"
        )

        self.returned_items.setText(
            f"Returned Items\n{returned}"
        )

    # OPEN ADD WINDOW
    def open_add_item(self):

        self.add_window = AddItemWindow(self)
        self.add_window.show()

    # OPEN SEARCH WINDOW
    def open_search_window(self):

        self.search_window = SearchWindow(self)
        self.search_window.show()


# ---------------- LOGIN FUNCTION ---------------- #

def login():

    username = username_input.text()
    password = password_input.text()

    if username == "admin" and password == "1234":

        global dashboard

        dashboard = Dashboard()
        dashboard.show()

        window.close()

    else:

        QMessageBox.warning(
            window,
            "Login Failed",
            "Invalid username or password."
        )


# ---------------- MAIN APPLICATION ---------------- #

app = QApplication(sys.argv)

# GLOBAL STYLE

app.setStyleSheet("""

QWidget{
    background-color: #f1f5f9;
    color: #0f172a;
    font-family: Segoe UI;
    font-size: 16px;
}

QLabel{
    color: #0f172a;
    font-size: 16px;
    font-weight: 600;
}

QLineEdit{
    background-color: white;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 12px;
    color: #0f172a;
    font-size: 15px;
}

QLineEdit:focus{
    border: 2px solid #3b82f6;
}

QTextEdit{
    background-color: white;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 12px;
    color: #0f172a;
    font-size: 15px;
}

QPushButton{
    background-color: #3b82f6;
    color: white;
    border-radius: 14px;
    padding: 12px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton:hover{
    background-color: #2563eb;
}

QTableWidget{
    background-color: white;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    gridline-color: #e2e8f0;
    color: #0f172a;
    font-size: 14px;
}

QHeaderView::section{
    background-color: #3b82f6;
    color: white;
    padding: 12px;
    border: none;
    font-size: 14px;
    font-weight: bold;
}

""")

# LOGIN WINDOW
window = QWidget()
window.setWindowTitle("UniTrack Login")
window.resize(950, 650)

# TITLE
title = QLabel("UniTrack Lost & Found Portal", window)
title.move(340, 170)
title.setFont(QFont("Segoe UI", 32, QFont.Bold))

# USERNAME LABEL
username_label = QLabel("Username", window)
username_label.move(270, 260)

# USERNAME INPUT
username_input = QLineEdit(window)
username_input.move(270, 295)
username_input.resize(400, 50)

# PASSWORD LABEL
password_label = QLabel("Password", window)
password_label.move(270, 380)

# PASSWORD INPUT
password_input = QLineEdit(window)
password_input.move(270, 415)
password_input.resize(400, 50)
password_input.setEchoMode(QLineEdit.Password)

# LOGIN BUTTON
login_button = QPushButton("Login", window)
login_button.move(350, 520)
login_button.resize(240, 60)

login_button.clicked.connect(login)

# SHOW WINDOW
window.show()

sys.exit(app.exec())