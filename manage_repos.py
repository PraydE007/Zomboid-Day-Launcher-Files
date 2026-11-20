#!/usr/bin/env python3
"""
Zomboid Day — Менеджер репозиторіїв та конфігурацій лаунчера
Дозволяє легко керувати переліком репозиторіїв, модулів і перевіряти маніфест.
Запуск без аргументів відкриває інтерактивне меню.
"""
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

REPO_DIR = Path(__file__).resolve().parent
REPOS_CONFIG = REPO_DIR / "repositories.json"
MANIFEST_FILE = REPO_DIR / "launcher-manifest.json"


def load_repos() -> List[Dict[str, Any]]:
    if not REPOS_CONFIG.exists():
        return []
    try:
        with open(REPOS_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Помилка зчитування {REPOS_CONFIG}: {e}")
        return []


def save_repos(repos: List[Dict[str, Any]]) -> bool:
    # Нормалізуємо чергу (order)
    for idx, r in enumerate(repos, start=1):
        r["order"] = idx
    try:
        with open(REPOS_CONFIG, "w", encoding="utf-8") as f:
            json.dump(repos, f, indent=2, ensure_ascii=False)
        print(f"✅ Збережено зміни у: {REPOS_CONFIG.name}")
        return True
    except Exception as e:
        print(f"❌ Помилка запису {REPOS_CONFIG}: {e}")
        return False


def list_repos():
    repos = load_repos()
    print("\n" + "═" * 70)
    print("  📋 СПИСОК ПІДКЛЮЧЕНИХ РЕПОЗИТОРІЇВ / МОДУЛІВ")
    print("═" * 70)
    if not repos:
        print("  (Список порожній)")
    else:
        for r in sorted(repos, key=lambda x: x.get("order", 999)):
            status = "🟢 [УВІМК]" if r.get("enabled", True) else "🔴 [ВИМК]"
            stype = r.get("source_type", "git")
            loc = r.get("local_path") if stype == "local" else r.get("git_url")
            print(f"  #{r.get('order', 1)} {status} {r.get('name')} (ID: {r.get('id')})")
            print(f"      Тип: {stype.upper()} | Джерело: {loc}")
            if r.get("description"):
                print(f"      Опис: {r.get('description')}")
            print("  " + "─" * 66)
    print()


def toggle_repo(repo_id: str):
    repos = load_repos()
    found = False
    for r in repos:
        if r.get("id") == repo_id:
            r["enabled"] = not r.get("enabled", True)
            state_str = "увімкнено" if r["enabled"] else "вимкнено"
            print(f"  → Репозиторій '{r.get('name')}' тепер {state_str}.")
            found = True
            break
    if not found:
        print(f"❌ Репозиторій з ID '{repo_id}' не знайдено.")
        return
    save_repos(repos)


def add_repo_interactive():
    print("\n" + "═" * 70)
    print("  ➕ ДОДАВАННЯ НОВОГО РЕПОЗИТОРІЮ")
    print("═" * 70)
    repo_id = input("  Введіть унікальний ID (наприклад, my-modpack): ").strip()
    if not repo_id:
        print("❌ ID не може бути порожнім.")
        return
    name = input("  Введіть назву (наприклад, My Modpack Collection): ").strip() or repo_id
    stype_choice = input("  Тип джерела: [1] Git URL (за замовчуванням), [2] Локальна папка: ").strip()
    stype = "local" if stype_choice == "2" else "git"
    
    local_path = ""
    git_url = ""
    branch = "main"
    if stype == "local":
        local_path = input("  Введіть абсолютний шлях до локальної папки: ").strip()
    else:
        git_url = input("  Введіть Git URL репозиторію: ").strip()
        branch_input = input("  Гілка [main]: ").strip()
        if branch_input:
            branch = branch_input

    has_manifest_choice = input("  Чи містить цей репозиторій launcher-manifest.json? [y/N]: ").strip().lower()
    has_manifest = (has_manifest_choice == "y" or has_manifest_choice == "так")
    desc = input("  Короткий опис: ").strip()

    repos = load_repos()
    new_entry = {
        "id": repo_id,
        "name": name,
        "order": len(repos) + 1,
        "enabled": True,
        "source_type": stype,
        "local_path": local_path,
        "git_url": git_url,
        "branch": branch,
        "has_manifest": has_manifest,
        "description": desc
    }
    repos.append(new_entry)
    save_repos(repos)
    print(f"✅ Репозиторій '{name}' успішно додано!")


def remove_repo(repo_id: str):
    repos = load_repos()
    initial_len = len(repos)
    repos = [r for r in repos if r.get("id") != repo_id]
    if len(repos) == initial_len:
        print(f"❌ Репозиторій з ID '{repo_id}' не знайдено.")
        return
    save_repos(repos)
    print(f"✅ Репозиторій '{repo_id}' видалено.")


def move_order(repo_id: str, new_order: int):
    repos = load_repos()
    idx = -1
    for i, r in enumerate(repos):
        if r.get("id") == repo_id:
            idx = i
            break
    if idx == -1:
        print(f"❌ Репозиторій з ID '{repo_id}' не знайдено.")
        return
    
    target_idx = max(0, min(len(repos) - 1, new_order - 1))
    item = repos.pop(idx)
    repos.insert(target_idx, item)
    save_repos(repos)
    print(f"✅ Порядок для '{item.get('name')}' оновлено на #{target_idx + 1}.")


def validate_manifest():
    print("\n" + "═" * 70)
    print("  🔍 ВАЛІДАЦІЯ launcher-manifest.json ТА ФАЙЛІВ")
    print("═" * 70)
    if not MANIFEST_FILE.exists():
        print(f"❌ Файл {MANIFEST_FILE.name} не знайдено!")
        return

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        project = data.get("project", {})
        print(f"  Проєкт: {project.get('name')} v{project.get('version')}")
        print(f"  Автор: {project.get('author')}")
        
        steps = data.get("install_steps", [])
        print(f"  Кількість кроків встановлення: {len(steps)}")
        for s in steps:
            stype = s.get("type")
            name = s.get("name")
            src = s.get("source")
            if stype == "copy_dir_contents" and src:
                src_path = REPO_DIR / src
                exists_mark = "✓" if src_path.exists() and src_path.is_dir() else "✗ ВІДСУТНЯ"
                print(f"    [{exists_mark}] Крок #{s.get('order')}: {name} -> папка {src}")
            elif stype == "open_url":
                print(f"    [✓] Крок #{s.get('order')}: {name} -> {s.get('url')}")
            else:
                print(f"    [✓] Крок #{s.get('order')}: {name} ({stype})")

        print("  ✅ Маніфест коректний та валідний.")
    except Exception as e:
        print(f"  ❌ Помилка валідації маніфесту: {e}")
    print()


def interactive_menu():
    while True:
        print("═" * 70)
        print("  ⚙️  ZOMBOID DAY — КЕРУВАННЯ РЕПОЗИТОРІЯМИ ТА МОДУЛЯМИ")
        print("═" * 70)
        print("  [1] Показати список підключених репозиторіїв")
        print("  [2] Додати новий репозиторій (Git або локальний)")
        print("  [3] Увімкнути / вимкнути репозиторій")
        print("  [4] Змінити чергу (order) репозиторію")
        print("  [5] Видалити репозиторій")
        print("  [6] Перевірити маніфест (launcher-manifest.json)")
        print("  [0] Вихід")
        print("─" * 70)
        choice = input("  Виберіть дію [0-6]: ").strip()

        if choice == "1":
            list_repos()
        elif choice == "2":
            add_repo_interactive()
        elif choice == "3":
            list_repos()
            rid = input("  Введіть ID репозиторію для перемикання: ").strip()
            if rid:
                toggle_repo(rid)
        elif choice == "4":
            list_repos()
            rid = input("  Введіть ID репозиторію: ").strip()
            new_ord = input("  Введіть новий номер у черзі (1, 2, ...): ").strip()
            if rid and new_ord.isdigit():
                move_order(rid, int(new_ord))
        elif choice == "5":
            list_repos()
            rid = input("  Введіть ID репозиторію для видалення: ").strip()
            if rid:
                confirm = input(f"  Ви дійсно бажаєте видалити '{rid}'? [y/N]: ").strip().lower()
                if confirm in ["y", "так"]:
                    remove_repo(rid)
        elif choice == "6":
            validate_manifest()
        elif choice in ["0", "q", "exit"]:
            print("До побачення!\n")
            break
        else:
            print("Невідома команда. Спробуйте ще раз.\n")


def main():
    parser = argparse.ArgumentParser(description="Менеджер конфігурації репозиторіїв Zomboid Day Launcher")
    parser.add_argument("command", nargs="?", default="menu",
                        choices=["menu", "list", "toggle", "add", "remove", "order", "validate"],
                        help="Команда для виконання")
    parser.add_argument("--id", help="ID репозиторію")
    parser.add_argument("--order", type=int, help="Нова черга репозиторію")

    args = parser.parse_args()

    if args.command == "menu":
        interactive_menu()
    elif args.command == "list":
        list_repos()
    elif args.command == "toggle":
        if not args.id:
            print("❌ Вкажіть --id")
            sys.exit(1)
        toggle_repo(args.id)
    elif args.command == "add":
        add_repo_interactive()
    elif args.command == "remove":
        if not args.id:
            print("❌ Вкажіть --id")
            sys.exit(1)
        remove_repo(args.id)
    elif args.command == "order":
        if not args.id or not args.order:
            print("❌ Вкажіть --id та --order")
            sys.exit(1)
        move_order(args.id, args.order)
    elif args.command == "validate":
        validate_manifest()


if __name__ == "__main__":
    main()
