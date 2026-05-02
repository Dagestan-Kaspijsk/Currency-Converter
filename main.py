import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Настройки
HISTORY_FILE = 'history.json'
API_URL = 'https://v6.exchangerate-api.com/v6/YOUR_API_KEY/latest/USD'

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.currencies = ['USD', 'EUR', 'GBP', 'JPY', 'RUB', 'CNY']

        # Виджеты
        ttk.Label(root, text="Из:").grid(row=0, column=0, padx=5, pady=5)
        self.from_currency = ttk.Combobox(root, values=self.currencies)
        self.from_currency.set('USD')
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="В:").grid(row=1, column=0, padx=5, pady=5)
        self.to_currency = ttk.Combobox(root, values=self.currencies)
        self.to_currency.set('EUR')
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(root, text="Сумма:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(root)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        self.convert_btn = ttk.Button(root, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(root, text="Результат: ")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Таблица истории
        self.history_tree = ttk.Treeview(root, columns=('from', 'to', 'amount', 'result'), show='headings')
        self.history_tree.heading('from', text='Из')
        self.history_tree.heading('to', text='В')
        self.history_tree.heading('amount', text='Сумма')
        self.history_tree.heading('result', text='Результат')
        self.history_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Загрузка истории
        self.load_history()

    def validate_input(self):
        amount = self.amount_entry.get()
        if not amount.replace('.', '', 1).isdigit():
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return False
        if float(amount) <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше 0")
            return False
        return True

    def convert(self):
        if not self.validate_input():
            return

        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        amount = float(self.amount_entry.get())

        try:
            response = requests.get(API_URL.replace('USD', from_cur))
            data = response.json()
            if data['result'] != 'success':
                raise Exception("Ошибка API")
            
            rate = data['conversion_rates'].get(to_cur)
            if rate is None:
                raise Exception(f"Курс для {to_cur} не найден")

            result = amount * rate
            self.result_label.config(text=f"Результат: {result:.2f} {to_cur}")

            # Сохранение в историю
            self.add_to_history(from_cur, to_cur, amount, result)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить курс: {e}")

    def add_to_history(self, from_cur, to_cur, amount, result):
        history = self.load_history()
        
        history.append({
            'from': from_cur,
            'to': to_cur,
            'amount': amount,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
        self.update_history_view()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                return json.load(f)
        return []

    def update_history_view(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
            
        for item in self.load_history():
            self.history_tree.insert('', 'end', values=(item['from'], item['to'], f"{item['amount']:.2f}", f"{item['result']:.2f}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()