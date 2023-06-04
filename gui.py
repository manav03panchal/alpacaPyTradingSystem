import sys
import threading
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject, QTimer
import keys
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, CryptoLatestQuoteRequest
from alpaca.common import exceptions
from alpaca.trading.client import TradingClient

class LivePriceThread(QThread):
    live_price_updated = pyqtSignal(str)

    def __init__(self, symbol, asset_type):
        super().__init__()
        self.symbol = symbol
        self.asset_type = asset_type
        self.trading_client = TradingClient(keys.KEY, keys.SECRET)
        self.running = True

    def run(self):
        if self.asset_type == "Stock":
            try:
                if self.trading_client.get_asset(self.symbol).tradable:
                    self.show_stock_live_price(self.symbol)
                else:
                    self.live_price_updated.emit(f"Symbol '{self.symbol}' is not tradable as a stock.")
            except exceptions.APIError:
                self.live_price_updated.emit(f"Symbol '{self.symbol}' not found.")
        elif self.asset_type == "Crypto":
            self.show_crypto_live_price(self.symbol)

    def show_crypto_live_price(self, symbol):
        client = CryptoHistoricalDataClient()
        while self.running:
            try:
                latest_quote = client.get_crypto_latest_quote(CryptoLatestQuoteRequest(symbol_or_symbols=[symbol]))
                latest_ask_price = latest_quote[symbol].ask_price
                self.live_price_updated.emit(f"{symbol}: ${latest_ask_price}")
                self.msleep(1000)  # Sleep for 1 second
            except exceptions.APIError as e:
                self.live_price_updated.emit(f"Error fetching live price: {e}")
                break

    def show_stock_live_price(self, symbol):
        client = StockHistoricalDataClient(keys.KEY, keys.SECRET)
        request_params = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
        while self.running:
            try:
                symbol_quotes = client.get_stock_latest_quote(request_params)
                latest_ask_price = symbol_quotes[symbol].ask_price
                self.live_price_updated.emit(f"{symbol}: ${latest_ask_price}")
                self.msleep(1000)  # Sleep for 1 second
            except exceptions.APIError as e:
                self.live_price_updated.emit(f"Error fetching live price: {e}")
                break
    
    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    def stop(self):
        self.running = False

class LivePriceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Price Viewer")
        self.layout = QVBoxLayout()

        self.symbol_label = QLabel("Enter Ticker Symbol:")
        self.symbol_input = QLineEdit()
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItem("Stock")
        self.asset_type_combo.addItem("Crypto")
        self.price_label = QLabel("")

        self.fetch_button = QPushButton("Fetch Live Price")
        self.fetch_button.clicked.connect(self.fetch_live_price)

        self.layout.addWidget(self.symbol_label)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.asset_type_combo)
        self.layout.addWidget(self.price_label)
        self.layout.addWidget(self.fetch_button)
        self.setLayout(self.layout)

        self.live_price_thread = None

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
        self.live_price_thread.start()

    @pyqtSlot(str)
    def update_live_price(self, price):
        self.price_label.setText(price)

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
