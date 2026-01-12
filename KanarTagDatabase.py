import math
import os
import requests
import json
import PyQt6
from pyairtable import *
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

AIRTABLE_API_KEY = ''

def load_api_key():
    global AIRTABLE_API_KEY
    f = open("./api.txt","r")
    AIRTABLE_API_KEY = f.read()
    f.close()

class AirtableTag:
    def __init__(self, api_key: str, base_id: str, table_name: str):    
        """
        Initialize Airtable client.
        :param api_key: Airtable API key (string)
        :param base_id: Airtable Base ID (string)
        :param table_name: Airtable Table Name (string)
        """
        if not all([api_key, base_id, table_name]):
            raise ValueError("API key, Base ID, and Table Name must be provided.")
        
        self.table = Table(api_key, base_id, table_name)
    def fetch_data(self, filters: dict = None, max_records: int = 100):
        """
        Fetch data from Airtable with optional filters.
        :param filters: Dictionary of field-value pairs to filter records.
        :param max_records: Maximum number of records to fetch.
        :return: List of record dictionaries.
        """
        try:
            if filters:
                # Build Airtable formula for filtering
                formula = match(filters)
                records = self.table.all(formula=formula, max_records=max_records)
            else:
                records = self.table.all(max_records=max_records)

            # Extract only the fields for cleaner output
            return [record["fields"] for record in records]

        except Exception as e:
            print(f"Error fetching data from Airtable: {e}")
            return []

class ApiViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KANAR Tag Database")
        self.resize(600, 400)

        # Layout
        layout = QVBoxLayout(self)
        
        # Button to fetch data
        self.fetch_button = QPushButton("Grab Tag Data")
        self.fetch_button.clicked.connect(self.fetch_data)
        layout.addWidget(self.fetch_button)

        # Table to display data
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)


    def fetch_data(self):

        load_api_key()

        BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appswDASXoosJEY2V")
        TABLE_NAME = "tblN9Rps7VLx59JL0"

        client = AirtableTag(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
        data = client.fetch_data()


        # Set table headers based on keys of first record
        headers = list(data[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))

        # Populate table
        for row_idx, record in enumerate(data):
            for col_idx, key in enumerate(headers):
                value = str(record.get(key, ""))
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ApiViewer()
    viewer.show()

    sys.exit(app.exec())
    
