# initializer.py
# Программа для создания папки нового соревнования и копирования шаблонов

import sys
import os
import shutil
import re
import datetime
import json # <--- Добавлен импорт JSON
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QDateEdit, QDialogButtonBox,
    QWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QDate, Qt, QDateTime # <--- Добавлен QDateTime

class InitializerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Инициализатор Соревнования FAST 2")
        self.setMinimumWidth(500)

        # --- Определение пути к ИСХОДНОЙ папке FAST_2_data ---
        # Этот код определяет, где ИСКАТЬ папку FAST_2_data
        # (ОНА ДОЛЖНА БЫТЬ РЯДОМ С .PY ИЛИ .EXE ИНИЦИАЛИЗАТОРА)
# В __init__ класса InitializerDialog

        # --- Определение пути к ИСХОДНОЙ папке FAST_2_data ---
        if getattr(sys, 'frozen', False):
            # Запущено как собранное приложение (.exe)
            self.application_path = os.path.dirname(sys.executable) # <--- Сохраняем в self.application_path
            print(f"Initializer: Режим .exe. Путь приложения: {self.application_path}")
        elif __file__:
            # Запущено как обычный скрипт (.py)
            self.application_path = os.path.dirname(os.path.abspath(__file__)) # <--- Сохраняем в self.application_path
            print(f"Initializer: Режим .py. Путь скрипта: {self.application_path}")
        else:
             # Резервный вариант
             self.application_path = os.getcwd() # <--- Сохраняем в self.application_path
             print(f"Initializer: Не удалось определить путь. Используется CWD: {self.application_path}")

        self.source_dir_name = "FAST_2_data"
        # Ищем папку FAST_2_data ОТНОСИТЕЛЬНО найденного пути
        self.source_path = os.path.join(self.application_path, self.source_dir_name) # <--- Используем локальную переменную или self.application_path
        print(f"Initializer: Ожидаемый путь к {self.source_dir_name}: {self.source_path}")
        print(f"Initializer: Существует ли папка {self.source_dir_name}? {'Да' if os.path.isdir(self.source_path) else 'НЕТ!'}")
        # --- Конец определения пути ---


        self.source_dir_name = "FAST_2_data"
        # Ищем папку FAST_2_data ОТНОСИТЕЛЬНО найденного пути application_path
        self.source_path = os.path.join(self.application_path, self.source_dir_name)
        print(f"Initializer: Ожидаемый путь к {self.source_dir_name}: {self.source_path}")
        # Добавим проверку сразу для отладки
        print(f"Initializer: Существует ли папка {self.source_dir_name} по этому пути? {'Да' if os.path.isdir(self.source_path) else 'НЕТ!'}")
        # --- Конец определения пути ---

        # --- UI Elements ---
        layout = QVBoxLayout(self)

        # Название соревнования
        self.name_edit = QLineEdit()
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название соревнования:"))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Дата соревнования
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата соревнования:"))
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Выбор директории назначения
        self.target_dir_edit = QLineEdit()
        self.target_dir_edit.setPlaceholderText("Выберите папку, ГДЕ будет создана папка соревнования")
        self.target_dir_edit.setReadOnly(True)
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self._browse_directory)
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Создать папку ВНУТРИ:"))
        target_layout.addWidget(self.target_dir_edit)
        target_layout.addWidget(browse_btn)
        layout.addLayout(target_layout)

        # Кнопки OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.process_creation)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)



    def _browse_directory(self):
        """Открывает диалог выбора директории."""
        # Используем self.application_path как стартовую директорию
        directory = QFileDialog.getExistingDirectory(self,
                                                     "Выберите папку назначения",
                                                     self.application_path) # <--- ИЗМЕНЕНО ЗДЕСЬ
        if directory:
            self.target_dir_edit.setText(directory)

    def _sanitize_filename(self, name):
        """Очищает строку для использования в имени файла/папки."""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = re.sub(r'[ .]+', '_', name)
        name = name.strip('_')
        return name

    def process_creation(self):
        """Основная логика проверки и создания папки соревнования."""
        event_name = self.name_edit.text().strip()
        event_date_q = self.date_edit.date()
        target_base_dir = self.target_dir_edit.text().strip()

        # 1. --- Валидация введенных данных ---
        if not event_name:
            QMessageBox.warning(self, "Ошибка ввода", "Введите название соревнования.")
            return
        if not event_date_q.isValid():
            QMessageBox.warning(self, "Ошибка ввода", "Выберите корректную дату соревнования.")
            return
        if not target_base_dir or not os.path.isdir(target_base_dir):
            QMessageBox.warning(self, "Ошибка ввода", "Выберите существующую папку назначения.")
            return

        event_date_str = event_date_q.toString("dd-MM-yyyy")
        sanitized_name = self._sanitize_filename(event_name)
        if not sanitized_name:
            QMessageBox.warning(self, "Ошибка ввода", "Название соревнования содержит недопустимые символы или пустое после очистки.")
            return

        # 2. --- Формирование путей ---
        event_folder_name = f"{sanitized_name}_{event_date_str}"
        destination_path = os.path.join(target_base_dir, event_folder_name)
        print(f"Источник: {self.source_path}")
        print(f"Назначение: {destination_path}")

        # 3. --- Проверка существования папки назначения ---
        if os.path.exists(destination_path):
            QMessageBox.critical(self, "Ошибка", f"Папка '{event_folder_name}' уже существует в выбранной директории.\nУдалите ее или выберите другое имя/дату/место.")
            return

        # 4. --- Проверка наличия исходной папки и критических файлов/папок ---
        critical_errors = []
        warnings = []

        if not os.path.isdir(self.source_path):
            critical_errors.append(f"Не найдена папка с шаблонами: '{self.source_dir_name}' рядом со скриптом.")
        else:
            data_subdir = os.path.join(self.source_path, "data")
            race_v1_file_src = os.path.join(data_subdir, "race_v1.json") # Путь к исходному файлу
            exe_file_src = os.path.join(self.source_path, "FAST_2.exe")

            if not os.path.isdir(data_subdir):
                critical_errors.append(f"Отсутствует обязательная папка 'data' внутри '{self.source_dir_name}'.")
            elif not os.path.isfile(race_v1_file_src):
                critical_errors.append(f"Отсутствует обязательный файл 'race_v1.json' внутри папки 'data'.")

            if not os.path.isfile(exe_file_src):
                critical_errors.append(f"Отсутствует обязательный файл 'FAST_2.exe' внутри '{self.source_dir_name}'.")

            sounds_subdir = os.path.join(self.source_path, "sounds")
            icons_subdir = os.path.join(self.source_path, "icons")

            if not os.path.isdir(sounds_subdir):
                warnings.append(f"Необязательная папка 'sounds' не найдена в '{self.source_dir_name}'.")
            if not os.path.isdir(icons_subdir):
                warnings.append(f"Необязательная папка 'icons' не найдена в '{self.source_dir_name}'.")

        if critical_errors:
            QMessageBox.critical(self, "Критическая Ошибка", "Не найдены обязательные файлы/папки для создания соревнования:\n\n" + "\n".join(critical_errors) + "\n\nПрограмма будет закрыта.")
            self.reject()
            QApplication.quit()
            return

        # 5. --- Создание папки и копирование ---
        try:
            print(f"Создание папки: {destination_path}")
            os.makedirs(destination_path)

            print("Копирование содержимого...")
            for item_name in os.listdir(self.source_path):
                source_item = os.path.join(self.source_path, item_name)
                destination_item = os.path.join(destination_path, item_name)

                try:
                    if os.path.isdir(source_item):
                        if item_name in ["sounds", "icons"] and not os.path.exists(source_item):
                             print(f"Пропуск копирования отсутствующей папки: {item_name}")
                             continue
                        print(f"  Копирование папки: {item_name}")
                        shutil.copytree(source_item, destination_item)
                    elif os.path.isfile(source_item):
                        print(f"  Копирование файла: {item_name}")
                        shutil.copy2(source_item, destination_item)
                except Exception as copy_err:
                    raise OSError(f"Ошибка при копировании '{item_name}': {copy_err}")

            # 6. --- Переименование .exe файла ---
            copied_exe_path = os.path.join(destination_path, "FAST_2.exe")
            new_exe_name = f"{event_folder_name}.exe"
            new_exe_path = os.path.join(destination_path, new_exe_name)

            if os.path.exists(copied_exe_path):
                print(f"Переименование '{copied_exe_path}' в '{new_exe_path}'")
                os.rename(copied_exe_path, new_exe_path)
            else:
                warnings.append("Скопированный файл FAST_2.exe не найден для переименования.")

            # 7. --- Обновление данных в race_v1.json ---
            race_v1_file_dest = os.path.join(destination_path, "data", "race_v1.json")
            if os.path.exists(race_v1_file_dest):
                print(f"Обновление метаданных в: {race_v1_file_dest}")
                try:
                    with open(race_v1_file_dest, 'r', encoding='utf-8') as f:
                        race_data = json.load(f)

                    # Убедимся, что структура 'meta' существует
                    if 'meta' not in race_data or not isinstance(race_data.get('meta'), dict):
                        race_data['meta'] = {} # Создаем, если нет

                    # Обновляем поля
                    race_data['meta']['name'] = event_name # Используем оригинальное имя
                    race_data['meta']['date'] = event_date_str
                    race_data['meta']['created_at'] = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                    # Убедимся, что версия равна 1 для нового соревнования
                    race_data['meta']['version'] = 1

                    # Перезаписываем файл с обновленными данными
                    with open(race_v1_file_dest, 'w', encoding='utf-8') as f:
                        json.dump(race_data, f, indent=4, ensure_ascii=False, default=str)
                    print("  Метаданные успешно обновлены.")

                except json.JSONDecodeError as json_err:
                    warnings.append(f"Не удалось прочитать или обновить race_v1.json (ошибка JSON): {json_err}")
                except IOError as io_err:
                    warnings.append(f"Не удалось прочитать или записать race_v1.json (ошибка ввода/вывода): {io_err}")
                except Exception as update_err:
                    warnings.append(f"Не удалось обновить race_v1.json (неизвестная ошибка): {update_err}")
            else:
                warnings.append("Скопированный файл race_v1.json не найден для обновления метаданных.")


            # 8. --- Финальные сообщения ---
            final_message = f"Папка соревнования '{event_folder_name}' успешно создана в:\n{target_base_dir}\n\nФайл программы переименован в:\n{new_exe_name}"
            if warnings:
                final_message += "\n\nПредупреждения:\n" + "\n".join(warnings)

            QMessageBox.information(self, "Успех!", final_message)
            self.accept()

        except OSError as e:
            QMessageBox.critical(self, "Ошибка Файловой Системы", f"Произошла ошибка при создании папки или копировании файлов:\n{e}\n\nВозможно, папка назначения уже существует или нет прав на запись.")
            if os.path.exists(destination_path):
                try: shutil.rmtree(destination_path); print(f"Удалена частично созданная папка: {destination_path}")
                except Exception as remove_err: print(f"Не удалось удалить частично созданную папку: {remove_err}")
        except Exception as e:
             QMessageBox.critical(self, "Неизвестная Ошибка", f"Произошла непредвиденная ошибка:\n{e}")


# --- Точка входа в программу ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = InitializerDialog()
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        print("Инициализация завершена успешно.")
    else:
        print("Инициализация отменена пользователем или произошла ошибка.")

    sys.exit()