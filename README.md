# Zomboid-Day-Launcher-Files

Репозиторій основних компонентів та налаштувань для проєкту **Zomboid Day**.

## 📌 Опис структури та маніфесту `launcher-manifest.json`

Лаунчер Zomboid Day зчитує файл `launcher-manifest.json` для автоматичного визначення:
1. **Загальної версії проєкту** (`project.version`)
2. **Черги та правил встановлення** (`install_steps` із полем `order`)
3. **Цільових шляхів призначення** (підтримуються змінні на зразок `{GAME_DIR}`, `{USER_ZOMBOID_DIR}`, `{MODS_DIR}`)
4. **Валідації встановлення** (`validation.required_files`)
5. **Параметрів запуску** (`launch.default_executable` та `launch.debug_executable`)

### 🗂 Структура репозиторію:
* `launcher-manifest.json` — конфігураційний маніфест лаунчера
* `game-configuration-files/` — оптимізовані bat-файли та конфігурація JVM:
  * `ProjectZomboid64.bat` — скрипт стандартного запуску (виділення пам'яті 8G–12G, ZGC, агент zbNative)
  * `ProjectZomboid64ShowConsole.bat` — скрипт дебаг-запуску з увімкненою консоллю та прапорцем `-debug`
  * `ProjectZomboid64.json` — налаштування classpath, vmArgs та GC
* `ZombieBuddy/`:
  * `ZombieBuddy.jar` — Java bytecode agent
  * `zbNative.dll` — нативна бібліотека для завантаження агента в JVM

### ⚙️ Додавання нових кроків встановлення
Щоб додати новий мод, патч або набір текстур:
1. Додайте папку з файлами до репозиторію.
2. Додайте запис до масиву `install_steps` у `launcher-manifest.json` із відповідним номером `order`.
3. Оновіть номер версії `project.version`.
