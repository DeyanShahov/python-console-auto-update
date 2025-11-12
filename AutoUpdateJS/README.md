# AutoUpdate JS

Автоматична система за обновяване на JavaScript/Node.js приложения от GitHub. Позволява сигурно изтегляне и прилагане на ъпдейти с backup на потребителски данни.

## 🚀 Основни възможности

- **Автоматична проверка за ъпдейти** - Проверка за нови версии от GitHub
- **Сигурни обновявания** - Backup и restore на потребителски данни
- **GitHub интеграция** - Директна работа с GitHub repositories и branches
- **CLI инструмент** - Command-line интерфейс за ръчно управление
- **Build процес интеграция** - Лесна интеграция в npm scripts
- **Cross-platform** - Работи на Windows, Linux и macOS
- **Promise-based** - Модерни async/await операции

## 📦 Инсталация

```bash
npm install autoupdate-js
```

Или копирайте папката `AutoUpdateJS` директно в проекта си.

## ⚡ Бърз старт

### 1. Настройка в package.json

```json
{
  "scripts": {
    "build": "node AutoUpdateJS/src/cli/check-updates.js && npm run build-app",
    "start": "node AutoUpdateJS/src/cli/check-updates.js && node app.js",
    "check-updates": "node AutoUpdateJS/src/cli/check-updates.js",
    "apply-updates": "node AutoUpdateJS/src/cli/check-updates.js --apply"
  }
}
```

### 2. Конфигурация чрез environment variables

```bash
export AUTOUPDATE_GITHUB_OWNER="your-github-username"
export AUTOUPDATE_GITHUB_REPO="AI-Online-Radio"
export AUTOUPDATE_PRODUCTION_BRANCH="user-branch"
export AUTOUPDATE_DEVELOPMENT_BRANCH="main-dev"
export AUTOUPDATE_USER_DATA_PATHS="data/,uploads/,config/"
```

### 3. Използване в код

```javascript
import { AutoUpdateService, AutoUpdateConfig } from './AutoUpdateJS/index.js';

// Конфигурация
const config = new AutoUpdateConfig({
  githubOwner: 'your-github-username',
  githubRepo: 'AI-Online-Radio',
  productionBranch: 'user-branch',
  developmentBranch: 'main-dev',
  userDataPaths: ['data/', 'uploads/'],
  versionFilePath: 'version.json'
});

// Създаване на service
const updateService = new AutoUpdateService(config);

// Проверка за ъпдейти
const result = await updateService.checkForUpdates();
if (result.hasUpdate) {
  console.log(`Налична е нова версия: ${result.newVersion.version}`);

  // Прилагане на ъпдейта
  const updateResult = await updateService.applyUpdate();
  if (updateResult.isSuccess) {
    console.log('✅ Ъпдейтът е приложен успешно!');
  }
}
```

## 📋 API Reference

### AutoUpdateService

Основният клас за управление на ъпдейти.

```javascript
const updateService = new AutoUpdateService(config);
```

#### Методи

- `checkForUpdates()` - Проверява за налични ъпдейти
- `applyUpdate()` - Прилага наличните ъпдейти
- `checkAndApplyUpdate()` - Проверява и прилага ъпдейти наведнъж
- `getCurrentVersion()` - Връща текущата версия
- `getLatestVersion()` - Връща последната версия от GitHub
- `cleanupBackups(count)` - Изчиства стари backup файлове

### AutoUpdateConfig

Клас за конфигурация.

```javascript
const config = new AutoUpdateConfig({
  githubOwner: 'username',
  githubRepo: 'repo-name',
  productionBranch: 'user-branch',
  userDataPaths: ['data/', 'uploads/']
});
```

#### Свойства

- `githubOwner` - GitHub потребителско име
- `githubRepo` - Име на repository
- `productionBranch` - Production branch за ъпдейти
- `developmentBranch` - Development branch (за справка)
- `userDataPaths` - Пътища до потребителски данни
- `versionFilePath` - Път до version.json файла
- `backupDirectory` - Директория за backups
- `httpTimeout` - HTTP timeout в ms
- `enableLogging` - Включване на logging

## 🛠️ CLI Инструмент

### Проверка за ъпдейти

```bash
# Проверка за налични ъпдейти
node AutoUpdateJS/src/cli/check-updates.js

# Прилагане на ъпдейти
node AutoUpdateJS/src/cli/check-updates.js --apply

# Детайлно логване
node AutoUpdateJS/src/cli/check-updates.js --verbose

# Използване на конфигурационен файл
node AutoUpdateJS/src/cli/check-updates.js --config my-config.json
```

### Опции

- `-c, --check` - Проверка за ъпдейти (default)
- `-a, --apply` - Прилагане на ъпдейти
- `-f, --config <file>` - Конфигурационен файл
- `-v, --verbose` - Детайлно логване
- `-h, --help` - Помощ

## ⚙️ Конфигурация

### Environment Variables

```bash
AUTOUPDATE_GITHUB_OWNER="username"
AUTOUPDATE_GITHUB_REPO="repo-name"
AUTOUPDATE_PRODUCTION_BRANCH="user-branch"
AUTOUPDATE_DEVELOPMENT_BRANCH="main-dev"
AUTOUPDATE_USER_DATA_PATHS="data/,uploads/"
AUTOUPDATE_VERSION_FILE_PATH="version.json"
AUTOUPDATE_BACKUP_DIRECTORY="backup/"
AUTOUPDATE_HTTP_TIMEOUT="30000"
AUTOUPDATE_ENABLE_LOGGING="true"
```

### Конфигурационен файл

```json
{
  "githubOwner": "username",
  "githubRepo": "repo-name",
  "productionBranch": "user-branch",
  "developmentBranch": "main-dev",
  "userDataPaths": ["data/", "uploads/"],
  "versionFilePath": "version.json",
  "backupDirectory": "backup/",
  "httpTimeout": 30000,
  "enableLogging": true
}
```

## 📁 Структура на проекта

```
AutoUpdateJS/
├── src/
│   ├── models/           # Модели за данни
│   │   ├── VersionInfo.js
│   │   ├── UpdateResult.js
│   │   └── UpdateCheckResult.js
│   ├── services/         # Основни услуги
│   │   ├── AutoUpdateService.js
│   │   ├── VersionProvider.js
│   │   ├── UpdateDownloader.js
│   │   └── UserDataManager.js
│   ├── config/           # Конфигурация
│   │   └── AutoUpdateConfig.js
│   ├── utils/            # Помощни функции
│   │   ├── logger.js
│   │   ├── httpClient.js
│   │   └── fileUtils.js
│   └── cli/              # CLI инструменти
│       └── check-updates.js
├── index.js              # Главен експорт
├── package.json          # npm конфигурация
└── README.md             # Тази документация
```

## 🔄 Процес на обновяване

1. **Проверка** - Сравняване на локална и отдалечена версия
2. **Backup** - Запазване на потребителски данни
3. **Изтегляне** - Download на ZIP от GitHub
4. **Разархивиране** - Extract на файловете
5. **Прилагане** - Копиране на новите файлове
6. **Обновяване** - Актуализиране на version.json
7. **Restore** - Възстановяване на потребителски данни

## 🛡️ Защита на данни

- **Backup преди обновяване** - Всички потребителски данни се запазват
- **Изключване на критични файлове** - User data и version.json се пропускат
- **Automatic rollback** - При грешка данните се възстановяват
- **Cleanup** - Временните файлове се изчистват

## 🚨 Важни бележки

- **Node.js 16+** - Изисква се Node.js версия 16 или по-нова
- **File permissions** - Приложението трябва да има права за писане
- **GitHub API limits** - Бъдете внимателни с честотата на заявките
- **Backup space** - Осигурете достатъчно дисково пространство

## 🔧 Интеграция в build процес

### Webpack Plugin

```javascript
class AutoUpdatePlugin {
  apply(compiler) {
    compiler.hooks.beforeCompile.tapAsync('AutoUpdatePlugin', async (params, callback) => {
      const { AutoUpdateService, AutoUpdateConfig } = await import('./AutoUpdateJS/index.js');

      const config = new AutoUpdateConfig({
        githubOwner: 'username',
        githubRepo: 'repo-name',
        productionBranch: 'user-branch'
      });

      const updateService = new AutoUpdateService(config);
      const result = await updateService.checkForUpdates();

      if (result.hasUpdate) {
        console.log('Applying update before build...');
        await updateService.applyUpdate();
      }

      callback();
    });
  }
}
```

### Gulp Task

```javascript
const gulp = require('gulp');
const { AutoUpdateService, AutoUpdateConfig } = require('./AutoUpdateJS/index.js');

gulp.task('check-updates', async function() {
  const config = new AutoUpdateConfig({
    githubOwner: 'username',
    githubRepo: 'repo-name',
    productionBranch: 'user-branch'
  });

  const updateService = new AutoUpdateService(config);
  const result = await updateService.checkForUpdates();

  if (result.hasUpdate) {
    await updateService.applyUpdate();
  }
});
```

## 📝 Примери за използване

### Express.js приложение

```javascript
const express = require('express');
const { AutoUpdateService, AutoUpdateConfig } = require('./AutoUpdateJS/index.js');

const app = express();

// Настройка на auto-update
const updateConfig = new AutoUpdateConfig({
  githubOwner: 'username',
  githubRepo: 'my-app',
  productionBranch: 'production',
  userDataPaths: ['data/', 'uploads/']
});

const updateService = new AutoUpdateService(updateConfig);

// Middleware за проверка на ъпдейти
app.use(async (req, res, next) => {
  const result = await updateService.checkForUpdates();
  if (result.hasUpdate) {
    res.locals.updateAvailable = result;
  }
  next();
});

app.listen(3000);
```

### Electron приложение

```javascript
const { app } = require('electron');
const { AutoUpdateService, AutoUpdateConfig } = require('./AutoUpdateJS/index.js');

app.whenReady().then(async () => {
  const updateConfig = new AutoUpdateConfig({
    githubOwner: 'username',
    githubRepo: 'my-electron-app',
    productionBranch: 'production',
    userDataPaths: [app.getPath('userData')]
  });

  const updateService = new AutoUpdateService(updateConfig);

  // Проверка при стартиране
  const result = await updateService.checkForUpdates();
  if (result.hasUpdate) {
    // Показване на диалог за обновяване
  }
});
```

## 🤝 Contributing

Системата е проектирана да бъде extensible. Можете да наследявате класовете и да добавяте custom функционалност.

## 📄 License

MIT License
