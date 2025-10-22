# Автоматично Обновяване на Приложения и Git Workflow (Общ Шаблон)

Този документ описва общ работен процес (workflow) за разработка и разпространение на приложения с автоматично обновяване, базиран на опита от проекта "Python Console App with Auto-Update from GitHub". Шаблонът е абстрактен и може да бъде адаптиран за различни езици и платформи.

## 1. Git Workflow: Разработчикски (Development) vs. Потребителски (Production) Версии

За да се осигури стабилност за крайните потребители и гъвкавост за разработчиците, се използва модел с два основни клона (branches):

*   **`main` branch (Development / Разработчикски клон):**
    *   Това е основният клон за активна разработка. Всички нови функции, поправки на бъгове и експерименти се правят първо тук.
    *   Може да съдържа незавършен или потенциално нестабилен код.
    *   **Не се използва за директно разпространение към потребители.**
    *   **Пример за commit message:** `Feature: Implement new XYZ functionality`, `Fix: Resolve bug in ABC module`, `Development: Refactor code for better performance`.

*   **`production` branch (Production / Потребителски клон):**
    *   Това е стабилният клон, който се разпространява към крайните потребители.
    *   Съдържа само тестван и готов за пускане код.
    *   **Потребителите получават ъпдейти само от този клон.**
    *   **Пример за commit message:** `Release vX.Y.Z: Add new feature ABC and fix bug XYZ`.

### Процес на работа:

1.  **Разработка:** Винаги работете в `main` branch.
    ```bash
    git checkout main
    # ... правите промени по кода ...
    git add .
    git commit -m "Development: Описание на промените"
    git push origin main
    ```
2.  **Тестване:** Тествайте новите функции и поправки в `main` branch.
3.  **Подготовка за Release (Пускане към потребители):** Когато сте сигурни, че промените в `main` са стабилни и готови за потребителите:
    ```bash
    git checkout production          # Превключете към production branch
    git merge main                   # Влейте промените от main в production
    # Преди да push-нете, увеличете номера на версията във файла за версии (виж т. 2)
    # ... актуализирайте version.json (или еквивалентен файл) ...
    git add version.json             # Добавете променения файл за версии
    git commit -m "Release vX.Y.Z: Описание на новите функции и поправки"
    git push origin production       # Push-нете към GitHub, за да задействате ъпдейт
    git checkout main                # Върнете се към development
    ```

## 2. Механизъм за Проверка и Прилагане на Обновявания

Приложението трябва да има вграден механизъм за проверка и прилагане на ъпдейти, който да не разчита на локално Git репозитори (тъй като потребителските инсталации са "чисти" и нямат `.git` папка).

*   **Файл за Версия (`version.json` или еквивалент):**
    *   Създайте файл (напр. `version.json`), който съдържа текущата версия на приложението (напр. `"version": "1.0.0"`) и друга мета информация (дата на последен ъпдейт, бележки за release).
    *   Този файл трябва да присъства както в `main`, така и в `production` клона.
    *   **Ключово:** Номерът на версията в този файл е "спусъкът" за ъпдейт.

*   **Логика за Проверка на Обновявания (в `updater.py` или еквивалент):**
    1.  **Изтегляне на отдалечена версия:** При стартиране, приложението изтегля файла за версия (напр. `version.json`) директно от `production` branch на GitHub (или друг източник).
    2.  **Сравнение на версиите:** Сравнява номера на версията от отдалечения файл с локалния.
    3.  **Задействане на ъпдейт:** Ако отдалечената версия е по-висока, се задейства процес на обновяване.
    4.  **Изтегляне на целия код:** Вместо `git pull`, изтеглете целия `production` branch като ZIP архив от GitHub.
    5.  **Разархивиране и копиране:** Разархивирайте архива във временна директория.
    6.  **Прилагане на промените:** Копирайте новите/обновени файлове от временната директория в основната директория на приложението.
    7.  **Актуализиране на локалния файл за версия:** След успешно обновяване, актуализирайте локалния файл за версия с новата информация от GitHub.

## 3. Защита на Потребителски Данни

Критично е потребителските данни (настройки, записи) да не се губят при обновяване.

*   **Отделна директория за данни (`user_data` или еквивалент):**
    *   Създайте специална директория (напр. `user_data`), в която приложението да съхранява всички потребителски файлове (напр. JSON файлове).
    *   Тази директория трябва да бъде изрично **изключена от процеса на копиране** по време на обновяване.
*   **Процес на Backup/Restore (в `updater.py` или еквивалент):**
    1.  **Backup:** Преди да започне копирането на новите файлове, направете backup на цялата директория с потребителски данни във временна backup папка.
    2.  **Restore:** След като новите файлове са копирани, възстановете потребителските данни от backup папката обратно в директорията за данни.
    3.  **Почистване:** Изтрийте временната backup папка.

## 4. Инсталация и Стартиране на Приложението

### Инсталационен Скрипт (One-Command Installation)

Предоставете лесен за изпълнение скрипт, който потребителите могат да използват за първоначална инсталация. Този скрипт трябва да:

1.  **Изтегли целия код** от `production` branch (напр. чрез `git clone` или изтегляне на ZIP).
2.  **Почисти ненужни файлове** (напр. `.git` папка, `install.py`, `install.ps1`, `README.md` - ако не са нужни в крайната инсталация).
3.  **Създаде стартов файл** (напр. `start.bat` за Windows, `start.sh` за Linux/macOS).

*   **Пример за Windows (PowerShell):**
    ```powershell
    iex (irm 'https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/production/install.ps1')
    ```
*   **Пример за Linux/macOS (Bash):**
    ```bash
    curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/production/install.py | python3
    ```

### Стартов Бутон/Скрипт (`start.bat` / `start.sh`)

Създайте прост скрипт, който потребителите могат да кликнат или изпълнят, за да стартират приложението. Този скрипт трябва да:

1.  Навигира до директорията на приложението (ако е необходимо).
2.  Изпълни основния файл на приложението (напр. `python main.py`, `java -jar app.jar`, `./app_executable`).
3.  Може да включва допълнителни команди за активиране на виртуални среди или други настройки.

*   **Пример за Windows (`start.bat`):**
    ```batch
    @echo off
    echo Starting [Your App Name]...
    python main.py
    pause
    ```
*   **Пример за Linux/macOS (`start.sh`):**
    ```bash
    #!/bin/bash
    echo "Starting [Your App Name]..."
    python3 main.py
    ```

## 5. Абстрактна Имплементация на Кода за Проверка на Обновявания

Ето как би изглеждала абстрактната логика за проверка на ъпдейти:

```python
# updater.py (или еквивалент)

import json
import os
import shutil
from urllib.request import urlopen, URLError
import zipfile
from datetime import datetime
import stat # За Windows readonly файлове

# --- КОНФИГУРАЦИЯ (ЗАМЕНЕТЕ С ВАШИТЕ ДАННИ) ---
REPO_OWNER = "YOUR_GITHUB_USERNAME"
REPO_NAME = "YOUR_GITHUB_REPO_NAME"
PRODUCTION_BRANCH = "production"
VERSION_FILE_NAME = "version.json"
USER_DATA_DIR = "user_data" # Директория за потребителски данни

GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{PRODUCTION_BRANCH}"
GITHUB_ZIP_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/{PRODUCTION_BRANCH}.zip"
# ---------------------------------------------

def _remove_readonly(func, path, _):
    """Помага за изтриване на readonly файлове на Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Грешка при премахване на {path}: {e}")

def get_local_version_info():
    """Взема локалната информация за версията."""
    if os.path.exists(VERSION_FILE_NAME):
        try:
            with open(VERSION_FILE_NAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"version": "0.0.0", "last_updated": "unknown", "commit_sha": ""}

def get_remote_version_info():
    """Взема отдалечената информация за версията от GitHub."""
    try:
        version_url = f"{GITHUB_RAW_URL}/{VERSION_FILE_NAME}"
        with urlopen(version_url) as response:
            return json.loads(response.read().decode('utf-8'))
    except (URLError, KeyError, json.JSONDecodeError) as e:
        print(f"Грешка при проверка за отдалечена версия: {e}")
        return None

def backup_user_data():
    """Прави backup на потребителските данни."""
    backup_dir = f"backup_{int(datetime.now().timestamp())}"
    os.makedirs(backup_dir, exist_ok=True)

    if os.path.exists(USER_DATA_DIR):
        for item_name in os.listdir(USER_DATA_DIR):
            src_path = os.path.join(USER_DATA_DIR, item_name)
            dst_path = os.path.join(backup_dir, item_name)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
        print(f"Backup на потребителски данни в {backup_dir}")
    return backup_dir

def restore_user_data(backup_dir):
    """Възстановява потребителските данни."""
    if not os.path.exists(backup_dir):
        return

    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    for item_name in os.listdir(backup_dir):
        src = os.path.join(backup_dir, item_name)
        dst = os.path.join(USER_DATA_DIR, item_name)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
    shutil.rmtree(backup_dir, onerror=_remove_readonly)
    print("Потребителските данни са възстановени. Backup директорията е изтрита.")

def apply_update(remote_version_info):
    """Изтегля и прилага ъпдейта."""
    print("Изтегляне на новата версия...")
    temp_zip_path = "update_temp.zip"
    temp_extract_dir = "temp_update_extract"

    try:
        with urlopen(GITHUB_ZIP_URL) as response, open(temp_zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Архивът е изтеглен.")

        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        print("Архивът е разархивиран.")

        extracted_folder_name = f"{REPO_NAME}-{PRODUCTION_BRANCH}"
        extracted_app_path = os.path.join(temp_extract_dir, extracted_folder_name)

        for item_name in os.listdir(extracted_app_path):
            source_path = os.path.join(extracted_app_path, item_name)
            destination_path = os.path.join('.', item_name)

            # Пропускаме директорията с потребителски данни и файла за версия
            if item_name == USER_DATA_DIR or item_name == VERSION_FILE_NAME:
                print(f"Пропускане на {item_name} (потребителски данни/файл за версия).")
                continue
            
            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
            elif os.path.isdir(source_path):
                if os.path.exists(destination_path):
                    shutil.rmtree(destination_path, onerror=_remove_readonly)
                shutil.copytree(source_path, destination_path)
            print(f"Обновен файл/директория: {item_name}")

        with open(VERSION_FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump(remote_version_info, f, indent=2)
        print("Локалният файл за версия е обновен.")
        return True
    except (URLError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print(f"Грешка при изтегляне/прилагане на обновяването: {e}")
        return False
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir, onerror=_remove_readonly)

def check_for_updates():
    """Основна функция за проверка и прилагане на ъпдейти."""
    print("Проверка за нови версии...")
    local_version_info = get_local_version_info()
    remote_version_info = get_remote_version_info()

    if remote_version_info:
        if remote_version_info.get("version") > local_version_info.get("version"):
            print(f"Намерена е нова версия: {remote_version_info.get('version')} (текуща: {local_version_info.get('version')})")
            print("Започваме обновяване...")
            backup_dir = backup_user_data()
            if apply_update(remote_version_info):
                restore_user_data(backup_dir)
                print("Обновяването е завършено успешно!")
            else:
                print("Грешка при обновяването. Възстановяване на данните...")
                restore_user_data(backup_dir)
                print("Обновяването е отменено.")
        else:
            print("Приложението е актуално.")
    else:
        print("Не може да се свърже с GitHub за проверка на обновления.")

# --- main.py (или еквивалент) ---
# import os
# import json
# from updater import check_for_updates
# from utils import USER_DATA_DIR # Ако USER_DATA_DIR е дефиниран в utils

# def get_app_display_version():
#     # Взема версията за показване в заглавието
#     try:
#         if os.path.exists("version.json"):
#             with open("version.json", 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#                 version = data.get('version', 'unknown')
#                 last_updated = data.get('last_updated', 'unknown')
#                 return version, last_updated
#     except (json.JSONDecodeError, KeyError):
#         pass
#     return "development", "unknown" # Default за development среда

# def main():
#     version, last_updated = get_app_display_version()
#     print(f"=== [Име на Вашето Приложение] v{version} ({last_updated}) ===\n")

#     if not os.path.exists(USER_DATA_DIR):
#         os.makedirs(USER_DATA_DIR)
#         print(f"Създадена директория за потребителски данни: '{USER_DATA_DIR}'")

#     check_for_updates()
#     # ... останалата логика на приложението ...

# if __name__ == "__main__":
#     main()
