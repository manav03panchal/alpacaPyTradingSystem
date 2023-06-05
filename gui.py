import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import keys
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, CryptoLatestQuoteRequest
from alpaca.common import exceptions
from alpaca.trading.client import TradingClient

ERROR_PREFIX = "ERROR: "
FETCHING_INTERVAL = 1000  # Fetching interval in milliseconds

class LivePriceThread(QThread):
    live_price_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, symbol, asset_type):
        super().__init__()
        self.symbol = symbol
        self.asset_type = asset_type
        self.trading_client = TradingClient(keys.KEY, keys.SECRET)
        self.running = True

    def run(self):
        try:
            if self.asset_type == "Stock":
                if self.trading_client.get_asset(self.symbol).tradable:
                    self.show_stock_live_price()
                else:
                    self.error_occurred.emit(f"Symbol '{self.symbol}' is not tradable as a stock.")
            elif self.asset_type == "Crypto":
                self.show_crypto_live_price()
        except exceptions.APIError as e:
            self.error_occurred.emit(str(e))

    def show_crypto_live_price(self):
        client = CryptoHistoricalDataClient()
        while self.running:
            try:
                latest_quote = client.get_crypto_latest_quote(CryptoLatestQuoteRequest(symbol_or_symbols=[self.symbol]))
                self.live_price_updated.emit(f"{self.symbol}: ${latest_quote[self.symbol].ask_price}")
                self.msleep(FETCHING_INTERVAL)
            except exceptions.APIError as e:
                self.error_occurred.emit(str(e))
                break

    def show_stock_live_price(self):
        client = StockHistoricalDataClient(keys.KEY, keys.SECRET)
        request_params = StockLatestQuoteRequest(symbol_or_symbols=[self.symbol])
        while self.running:
            try:
                symbol_quotes = client.get_stock_latest_quote(request_params)
                self.live_price_updated.emit(f"{self.symbol}: ${symbol_quotes[self.symbol].ask_price}")
                self.msleep(FETCHING_INTERVAL)
            except exceptions.APIError as e:
                self.error_occurred.emit(str(e))
                break

    def stop(self):
        self.running = False

class UpperCaseLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.setText(self.text().upper())
        self.setCursorPosition(len(self.text()))  # keep the cursor at the end of text

class LivePriceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard")
        self.layout = QVBoxLayout()

        # Create a horizontal layout for the label and line edit
        self.symbol_layout = QHBoxLayout()
        self.symbol_label = QLabel("Enter Ticker Symbol:")
        self.symbol_input = QLineEdit()
        self.symbol_input.textChanged.connect(lambda: self.symbol_input.setText(self.symbol_input.text().upper()))
        # Add the label and line edit to the horizontal layout
        self.symbol_layout.addWidget(self.symbol_label)
        self.symbol_layout.addWidget(self.symbol_input)

        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItem("Stock")
        self.asset_type_combo.addItem("Crypto")
        self.price_label = QLabel("")

        self.fetch_button = QPushButton("Fetch Live Price")
        self.fetch_button.clicked.connect(self.fetch_live_price)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(self.symbol_layout)
        self.layout.addWidget(self.asset_type_combo)
        self.layout.addWidget(self.price_label)
        self.layout.addWidget(self.fetch_button)
        self.setLayout(self.layout)

        self.live_price_thread = None

    @pyqtSlot()
    def force_uppercase(self):
        self.symbol_input.setText(self.symbol_input.text().upper())

    def fetch_live_price(self):
        symbol = self.symbol_input.text().strip().upper()
        asset_type = self.asset_type_combo.currentText()
        self.symbol_input.clear()
        self.price_label.setText("Fetching...")

        if self.live_price_thread and self.live_price_thread.isRunning():
            self.live_price_thread.stop()
            self.live_price_thread.wait()

        self.live_price_thread = LivePriceThread(symbol, asset_type)
        self.live_price_thread.live_price_updated.connect(self.update_live_price)
        self.live_price_thread.error_occurred.connect(self.show_error_message)
        self.live_price_thread.start()

    @pyqtSlot(str)
    def update_live_price(self, price):
        self.price_label.setText(price)

    @pyqtSlot(str)
    def show_error_message(self, error):
        QMessageBox.warning(self, "Error", error)

    def closeEvent(self, event):
        if self.live_price_thread and self.live_price_thread.isRunning():
            self.live_price_thread.stop()
            self.live_price_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = LivePriceWidget()
    widget.show()

    sys.exit(app.exec())
