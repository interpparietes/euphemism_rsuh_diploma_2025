import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QHBoxLayout, QFileDialog, QMessageBox)


class EuphemismLabeler(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Euphemism Labeler")
        self.setGeometry(100, 100, 600, 400)

        self.json_data = []
        self.current_text_idx = 0
        self.input_file_name = ""  # Для хранения имени входного файла
        self.output_file_name = ""  # Для хранения имени выходного файла
        self.selected_euphemism = None  # Для хранения выбранного эвфемизма

        # Layouts
        self.layout = QVBoxLayout()
        self.text_label = QLabel("Текст будет отображаться здесь")
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self.update_save_button_state)

        # Вопрос о эвфемизмах
        self.question_label = QLabel("Есть ли эвфемизмы в этом тексте?")
        self.yes_button = QPushButton("ДА")
        self.no_button = QPushButton("НЕТ")

        # Кнопка для возврата к предыдущему тексту
        self.previous_button = QPushButton("Предыдущий текст")
        self.previous_button.setEnabled(False)
        self.previous_button.clicked.connect(self.previous_text)

        # Кнопка для выбора файла
        self.load_button = QPushButton("Загрузить JSON файл")
        self.load_button.clicked.connect(self.load_json)

        # Кнопка для удаления текста
        self.delete_button = QPushButton("Удалить текст")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_text)

        # Кнопка для сохранения выделенного эвфемизма
        self.save_button = QPushButton("Сохранить выделенный эвфемизм")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_euphemism)

        # Кнопка для удаления выделенного эвфемизма
        self.remove_euphemism_button = QPushButton("Удалить эвфемизм")
        self.remove_euphemism_button.setEnabled(False)
        self.remove_euphemism_button.clicked.connect(self.remove_euphemism)

        # Кнопка для перехода к следующему тексту
        self.next_button = QPushButton("Следующий текст")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_text)

        # Кнопка для сохранения данных в файл
        self.save_data_button = QPushButton("Сохранить в файл")
        self.save_data_button.clicked.connect(self.save_json)

        # Добавление виджетов на экран
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.question_label)

        # Кнопки да/нет и возврат
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)
        button_layout.addWidget(self.previous_button)

        # Добавление кнопки удаления текста
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.remove_euphemism_button)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.save_data_button)  # Добавляем кнопку для сохранения данных

        # Привязка функций к кнопкам
        self.yes_button.clicked.connect(self.mark_euphemism)
        self.no_button.clicked.connect(self.no_euphemism)

        self.setLayout(self.layout)

    def load_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите JSON файл", "", "JSON Files (*.json)",
                                                   options=options)

        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)

            # Сохранение имени входного файла
            self.input_file_name = file_name
            self.current_text_idx = 0
            self.previous_button.setEnabled(False)  # Отключаем кнопку возврата
            self.next_text()

    def next_text(self):
        if self.current_text_idx < len(self.json_data):
            text_entry = self.json_data[self.current_text_idx]['text']
            self.text_label.setText(f"Текст {self.current_text_idx + 1}")
            self.text_edit.setText(text_entry)
            self.current_text_idx += 1
            self.next_button.setEnabled(False)
            self.previous_button.setEnabled(True)  # Активируем кнопку возврата
            self.delete_button.setEnabled(True)
            self.save_button.setEnabled(False)  # Отключаем кнопку сохранения
            self.remove_euphemism_button.setEnabled(False)  # Отключаем кнопку удаления эвфемизма

            # Проверяем наличие эвфемизма в тексте
            for euphemism in self.extract_euphemisms(text_entry):
                if euphemism in text_entry:
                    self.selected_euphemism = euphemism
                    break

            self.update_ui()  # Обновляем интерфейс

        else:
            QMessageBox.information(self, "Конец", "Больше текстов нет!")
            self.save_button.setEnabled(True)

    def previous_text(self):
        if self.current_text_idx > 1:
            self.current_text_idx -= 2  # Уменьшаем на 2, так как next_text увеличивает индекс на 1
            self.next_text()
        else:
            QMessageBox.information(self, "Предыдущий текст", "Вы уже на первом тексте.")

    def update_save_button_state(self):
        # Активируем кнопку сохранения, если выделен текст
        selected_text = self.text_edit.textCursor().selectedText()
        self.save_button.setEnabled(bool(selected_text))
        self.remove_euphemism_button.setEnabled(bool(self.selected_euphemism))  # Активируем кнопку удаления

    def mark_euphemism(self):
        self.question_label.setText("Выделите эвфемизм и нажмите 'Сохранить'.")
        self.update_save_button_state()  # Проверяем состояние кнопки сразу после изменения текста

    def no_euphemism(self):
        self.next_button.setEnabled(True)

    def save_euphemism(self):
        euphemism = self.text_edit.textCursor().selectedText()

        if euphemism:
            original_text = self.json_data[self.current_text_idx - 1]['text']
            marked_text = original_text.replace(euphemism, f"<euphemism>{euphemism}</euphemism>")
            self.json_data[self.current_text_idx - 1]['text'] = marked_text

            # Обновление выделенного эвфемизма
            self.selected_euphemism = euphemism  # Сохраняем новый эвфемизм
            self.text_edit.setText(original_text.replace(euphemism, f"<euphemism>{euphemism}</euphemism>"))
            self.save_button.setEnabled(False)  # Отключаем кнопку после сохранения
            self.next_button.setEnabled(True)  # Активируем кнопку следующего текста
            self.update_ui()  # Обновляем интерфейс

    def remove_euphemism(self):
        if self.selected_euphemism:
            original_text = self.json_data[self.current_text_idx - 1]['text']
            # Удаляем <euphemism> теги из текста
            cleaned_text = original_text.replace(f"<euphemism>{self.selected_euphemism}</euphemism>",
                                                 self.selected_euphemism)
            self.json_data[self.current_text_idx - 1]['text'] = cleaned_text
            self.text_edit.setText(cleaned_text)

            # Сбрасываем выбранный эвфемизм
            self.selected_euphemism = None

            # Обновляем состояние кнопок
            self.save_button.setEnabled(False)
            self.remove_euphemism_button.setEnabled(False)
            self.update_save_button_state()  # Проверяем состояние кнопки сохранения

    def delete_text(self):
        if len(self.json_data) > 0:
            del self.json_data[self.current_text_idx - 1]
            if len(self.json_data) == 0:
                QMessageBox.information(self, "Удаление текста", "Текст был успешно удален.")
                self.text_label.setText("Нет доступных текстов.")
                self.text_edit.clear()
                self.delete_button.setEnabled(False)
                self.previous_button.setEnabled(False)  # Отключаем кнопку возврата
                return

            if self.current_text_idx > len(self.json_data):
                self.current_text_idx -= 1

            if len(self.json_data) > 0:
                self.next_text()
            else:
                QMessageBox.information(self, "Удаление текста", "Текст был успешно удален.")
                self.text_label.setText("Нет доступных текстов.")
                self.text_edit.clear()
                self.delete_button.setEnabled(False)
                self.previous_button.setEnabled(False)  # Отключаем кнопку возврата

    def extract_euphemisms(self, text):
        return [euphemism.split("</euphemism>")[0] for euphemism in text.split("<euphemism>")[1:]]

    def save_json(self):
        self.output_file_name = self.generate_output_file_name()

        with open(self.output_file_name, 'w', encoding='utf-8') as file:
            json.dump(self.json_data, file, ensure_ascii=False, indent=4)

        QMessageBox.information(self, "Успех!", f"Данные успешно сохранены в {self.output_file_name}.")

    def generate_output_file_name(self):
        base_name = os.path.splitext(self.input_file_name)[0]
        return f"{base_name}_labeled.json"

    def update_ui(self):
        # Обновление интерфейса в зависимости от состояния
        if self.current_text_idx < len(self.json_data):
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

        if self.current_text_idx > 1:
            self.previous_button.setEnabled(True)
        else:
            self.previous_button.setEnabled(False)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    labeler = EuphemismLabeler()
    labeler.show()
    sys.exit(app.exec_())
