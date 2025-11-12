# AutoUpdate Python

Автоматична система за обновяване на Python приложения от GitHub. Позволява сигурно изтегляне и прилагане на ъпдейти с backup на потребителски данни.

## 🚀 Основни възможности

- **Автоматична проверка за ъпдейти** - Проверка за нови версии от GitHub
- **Сигурни обновявания** - Backup и restore на потребителски данни
- **GitHub интеграция** - Директна работа с GitHub repositories и branches
- **CLI инструмент** - Command-line интерфейс за ръчно управление
- **Python package** - Лесна инсталация и използване
- **Cross-platform** - Работи на Windows, Linux и macOS
- **Pure Python** - Само стандартната библиотека, без външни зависимости

## 📦 Инсталация

### От PyPI (когато бъде публикуван)
```bash
pip install autoupdate-python
```

### От source
```bash
git clone <repository-url>
cd AutoUpdatePython
pip install -e .
```

### Ръчно копиране
Копирайте папката `AutoUpdatePython/autoupdate` в проекта си.

## ⚡ Бърз старт

### 1. Настройка в Python проект

```python
# main.py
from autoupdate import AutoUpdateService, AutoUpdateConfig

# Конфигурация за AI-Online-Radio проект
config = AutoUpdateConfig(
    github_owner='your-github-username',
    github_repo='AI-Online-Radio',
    production_branch='user-branch',  # Само този branch се проверява!
    development_branch='main-dev',    # Игнорира се
    user_data_paths=['data/', 'uploads/', 'config/'],
    version_file_path='version.json'
)

# Създаване на service
updater = AutoUpdateService(config)

# Проверка при стартиране
result = updater.check_for_updates()
if result.has_update:
    print(f"Налична е нова версия: {result.new_version.version}")
    # Прилагане на ъпдейта
    update_result = updater.apply_update()
    if update_result.is_success:
        print("✅ Ъпдейтът е приложен успешно!")
```

### 2. CLI използване

```bash
# Проверка за ъпдейти
python -m autoupdate.cli.check_updates

# Автоматично прилагане
python -m autoupdate.cli.check_updates --apply

# С environment variables
export AUTOUPDATE_GITHUB_OWNER="username"
export AUTOUPDATE_GITHUB_REPO="AI-Online-Radio"
export AUTOUPDATE_PRODUCTION_BRANCH="user-branch"
python -m autoupdate.cli.check_updates
```

## 📋 API Reference

### AutoUpdateService

Основният клас за управление на ъпдейти.

```python
from autoupdate import AutoUpdateService, AutoUpdateConfig

config = AutoUpdateConfig(...)
updater = AutoUpdateService(config)
```

#### Методи

- `check_for_updates()` - Проверява за налични ъпдейти
- `apply_update()` - Прилага наличните ъпдейти
- `check_and_apply_update()` - Проверява и прилага ъпдейти наведнъж
- `get_current_version()` - Връща текущата версия
- `get_latest_version()` - Връща последната версия от GitHub
- `cleanup_backups(count)` - Изчиства стари backup файлове

### AutoUpdateConfig

Клас за конфигурация.

```python
config = AutoUpdateConfig(
    github_owner='username',
    github_repo='repo-name',
    production_branch='user-branch',
    user_data_paths=['data/', 'uploads/']
)
```

#### Параметри

- `github_owner` - GitHub потребителско име
- `github_repo` - Име на repository
- `production_branch` - Production branch за ъпдейти
- `development_branch` - Development branch (за справка)
- `user_data_paths` - Пътища до потребителски данни
- `version_file_path` - Път до version.json файла
- `backup_directory` - Директория за backups
- `http_timeout` - HTTP timeout в секунди
- `enable_logging` - Включване на logging

## ⚙️ Конфигурация

### Environment Variables

```bash
export AUTOUPDATE_GITHUB_OWNER="username"
export AUTOUPDATE_GITHUB_REPO="AI-Online-Radio"
export AUTOUPDATE_PRODUCTION_BRANCH="user-branch"
export AUTOUPDATE_DEVELOPMENT_BRANCH="main-dev"
export AUTOUPDATE_USER_DATA_PATHS="data/,uploads/"
export AUTOUPDATE_VERSION_FILE_PATH="version.json"
export AUTOUPDATE_BACKUP_DIRECTORY="backup/"
export AUTOUPDATE_HTTP_TIMEOUT="30"
export AUTOUPDATE_ENABLE_LOGGING="true"
```

### Конфигурационен файл

```python
# config.py
from autoupdate import AutoUpdateConfig

config = AutoUpdateConfig(
    github_owner='username',
    github_repo='AI-Online-Radio',
    production_branch='user-branch',
    development_branch='main-dev',
    user_data_paths=['data/', 'uploads/'],
    version_file_path='version.json',
    backup_directory='backup/',
    http_timeout=30,
    enable_logging=True
)
```

### Автоматично зареждане

```python
# От environment variables
config = AutoUpdateConfig.from_environment()

# От JSON файл
config = AutoUpdateConfig.from_file('config.json')
```

## 🛠️ CLI Инструмент

### Основни команди

```bash
# Проверка за ъпдейти (default)
python -m autoupdate.cli.check_updates

# Прилагане на ъпдейти
python -m autoupdate.cli.check_updates --apply

# Използване на конфигурационен файл
python -m autoupdate.cli.check_updates --config my-config.json

# Детайлно логване
python -m autoupdate.cli.check_updates --verbose
```

### Опции

- `-c, --check` - Проверка за ъпдейти (default)
- `-a, --apply` - Прилагане на ъпдейти
- `-f, --config <file>` - Конфигурационен файл
- `-v, --verbose` - Детайлно логване
- `-h, --help` - Помощ

## 📁 Структура на проекта

```
AutoUpdatePython/
├── autoupdate/
│   ├── __init__.py          # Главен експорт
│   ├── core.py              # VersionInfo, UpdateResult, UpdateCheckResult
│   ├── service.py           # AutoUpdateService
│   ├── version_provider.py  # VersionProvider
│   ├── downloader.py        # UpdateDownloader
│   ├── data_manager.py      # UserDataManager
│   └── config.py            # AutoUpdateConfig
├── cli/
│   └── check_updates.py     # CLI инструмент
├── examples/
│   ├── basic_usage.py       # Основен пример
│   └── flask_integration.py # Flask интеграция
├── setup.py                 # Python package setup
├── requirements.txt         # Dependencies
└── README.md                # Тази документация
```

## 🔄 Процес на обновяване

1. **Проверка** - Сравнява локална версия с `user-branch` на GitHub
2. **Backup** - Запазва потребителски данни в timestamped папки
3. **Download** - Изтегля ZIP от GitHub production branch
4. **Extract & Apply** - Разархивира и копира файлове (без user data)
5. **Update version.json** - Актуализира локалната версия
6. **Restore** - Възстановява потребителски данни
7. **Cleanup** - Изчиства временни файлове

## 🛡️ Защита на данни

- **Backup преди обновяване** - Всички потребителски данни се запазват
- **Изключване на критични файлове** - User data и version.json се пропускат
- **Automatic rollback** - При грешка данните се възстановяват
- **Cleanup** - Временните файлове се изчистват

## 🚨 Важни бележки

- **Python 3.8+** - Изисква се Python версия 3.8 или по-нова
- **File permissions** - Приложението трябва да има права за писане
- **GitHub API limits** - Бъдете внимателни с честотата на заявките
- **Backup space** - Осигурете достатъчно дисково пространство

## 🔧 Интеграция в различни Python проекти

### Flask приложение

```python
from flask import Flask
from autoupdate import AutoUpdateService, AutoUpdateConfig

app = Flask(__name__)

# Настройка на auto-update
config = AutoUpdateConfig(
    github_owner='username',
    github_repo='my-flask-app',
    production_branch='production',
    user_data_paths=['instance/', 'uploads/']
)

updater = AutoUpdateService(config)

@app.route('/check-updates')
def check_updates():
    result = updater.check_for_updates()
    if result.has_update:
        return f"Update available: {result.new_version.version}"
    return "App is up to date"

@app.route('/apply-update')
def apply_update():
    result = updater.apply_update()
    if result.is_success:
        return f"Update applied: {result.updated_version.version}"
    return f"Update failed: {result.error_message}"
```

### Django приложение

```python
# settings.py
AUTOUPDATE_CONFIG = {
    'github_owner': 'username',
    'github_repo': 'my-django-app',
    'production_branch': 'production',
    'user_data_paths': ['media/', 'static/uploads/'],
}

# management command
from django.core.management.base import BaseCommand
from autoupdate import AutoUpdateService, AutoUpdateConfig

class Command(BaseCommand):
    help = 'Check for and apply updates'

    def handle(self, *args, **options):
        config = AutoUpdateConfig(**AUTOUPDATE_CONFIG)
        updater = AutoUpdateService(config)

        result = updater.check_for_updates()
        if result.has_update:
            self.stdout.write(f"Update available: {result.new_version.version}")
            update_result = updater.apply_update()
            if update_result.is_success:
                self.stdout.write("Update applied successfully!")
            else:
                self.stderr.write(f"Update failed: {update_result.error_message}")
        else:
            self.stdout.write("App is up to date")
```

### Console приложение

```python
#!/usr/bin/env python3
import sys
from autoupdate import AutoUpdateService, AutoUpdateConfig

def main():
    config = AutoUpdateConfig.from_environment()
    updater = AutoUpdateService(config)

    # Check for updates on startup
    result = updater.check_for_updates()
    if result.has_update:
        print(f"Update available: {result.new_version.version}")
        response = input("Apply update? (y/N): ").strip().lower()
        if response == 'y':
            update_result = updater.apply_update()
            if update_result.is_success:
                print("Update applied successfully!")
                sys.exit(0)  # Restart application
            else:
                print(f"Update failed: {update_result.error_message}")
                sys.exit(1)

    # Continue with normal application logic
    print("Starting application...")

if __name__ == "__main__":
    main()
```

## 📝 Примери

Вижте папката `examples/` за пълни примери на интеграция.

## 🤝 Contributing

Системата е проектирана да бъде extensible. Можете да наследявате класовете и да добавяте custom функционалност.

## 📄 License

MIT License
