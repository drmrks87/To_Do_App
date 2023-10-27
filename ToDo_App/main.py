from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox, QCalendarWidget
from PyQt6.QtGui import QAction, QIcon
from win10toast import ToastNotifier
from datetime import datetime
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToDo App")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_todo_action = QAction(QIcon("icons/add.png"), "Add ToDo", self)
        add_todo_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_todo_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        edit_action = QAction(QIcon("icons/edit.png"), "Edit", self)
        edit_menu_item.addAction(edit_action)
        edit_action.triggered.connect(self.edit)

        delete_action = QAction(QIcon("icons/delete.png"), "Delete", self)
        edit_menu_item.addAction(delete_action)
        delete_action.triggered.connect(self.delete)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(('Id', 'Todo', 'Date'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create Toolbar and add Toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_todo_action)
        toolbar.addAction(search_action)
        toolbar.addAction(edit_action)
        toolbar.addAction(delete_action)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM todos")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add ToDo")
        self.setFixedWidth(350)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add To Do
        self.todo_name = QLineEdit()
        self.todo_name.setPlaceholderText("Add ToDo")
        layout.addWidget(self.todo_name)

        # Add Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.calendar_date)
        layout.addWidget(self.calendar)

        # Add submit button
        button = QPushButton("Add ToDo")
        button.clicked.connect(self.add_todo)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_todo(self):
        name = self.todo_name.text()
        date = self.calendar_date()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO todos (Todo, Date) VALUES (?, ?)", (name, date))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

    def calendar_date(self):
        dateselected = self.calendar.selectedDate()
        date_in_string = str(dateselected.toPyDate())
        return date_in_string


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search ToDo")
        self.setFixedWidth(350)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.todo_name = QLineEdit()
        self.todo_name.setPlaceholderText("Search ToDo")
        layout.addWidget(self.todo_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.todo_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM todos WHERE Todo = ?", (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update ToDo")
        self.setFixedWidth(350)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get To Do from selected row
        index = main_window.table.currentRow()
        todo_name = main_window.table.item(index, 1).text()

        # Get Id from selected row
        self.todo_id = main_window.table.item(index, 0).text()

        # Add To Do Name Widget
        self.todo_name = QLineEdit(todo_name)
        self.todo_name.setPlaceholderText("Add ToDo")
        layout.addWidget(self.todo_name)

        # Add Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.calendar_date)
        layout.addWidget(self.calendar)

        # Add submit button
        button = QPushButton("Update ToDo")
        button.clicked.connect(self.update_todo)
        layout.addWidget(button)

        self.setLayout(layout)

    def calendar_date(self):
        dateselected = self.calendar.selectedDate()
        date_in_string = str(dateselected.toPyDate())
        return date_in_string

    def update_todo(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE todos SET Todo = ?, Date = ? WHERE Id = ?",
                       (self.todo_name.text(), self.calendar_date(), self.todo_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete ToDo")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_todo)
        no.clicked.connect(self.close)

    def delete_todo(self):
        # Get selected row index and to do id
        index = main_window.table.currentRow()
        todo_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM todos WHERE Id = ?", (todo_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = '''
        This ToDo App was created to help you organise your ToDos.
        You can select a date until you want to finish your ToDo.
        '''
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
