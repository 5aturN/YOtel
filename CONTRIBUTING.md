# Вклад в проект

1. Обновить `develop` и создать `feature/<описание>`.
2. Делать небольшие коммиты с номером практической работы и конкретным результатом.
3. Перед слиянием выполнить `python -m unittest discover -s tests -v`, `python -m pytest -q`, `python -m ruff check src tests` и `python -m bandit -r src/yaotel -ll`.
4. Не коммитить реальные `.env`, API-ключи, SMTP-пароли или персональные данные.
5. Слить feature-ветку в `develop`, затем выпустить проверенный релиз из `main`.
