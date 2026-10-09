# Модульное тестирование

## Проверяемая функция

В `src/yaotel/pricing.py` реализован `PriceCalculator.calculate_total_kopecks`. Функция считает проживание в копейках, чтобы не использовать двоичную арифметику с `float`. Интервал проживания полуоткрытый: дата выезда не оплачивается. Для ночей, начинающихся в пятницу или субботу, применяется коэффициент 1,15.

## Набор проверок

| Сценарий | Ожидаемый результат | Тест |
|---|---:|---|
| Две будние ночи по 10 000 коп. | 20 000 коп. | `test_weekday_nights_use_base_rate` |
| Пятница–понедельник: две выходные и одна будняя ночь | 33 000 коп. | `test_friday_and_saturday_nights_use_weekend_rate` |
| Выезд в субботу после одной пятничной ночи | 11 500 коп. | `test_checkout_is_exclusive` |
| Нулевая или обратная длительность проживания | `ValueError` | `test_rejects_empty_or_reversed_stay` |
| Нулевая цена | `ValueError` | `test_rejects_non_positive_rate` |
| Округление до копейки | целое число копеек | `test_rounds_to_a_whole_kopeck` |

## Запуск

```powershell
python -m unittest discover -s tests -v
python -m pytest -q
```

Последняя локальная проверка: **7 тестов пройдены** (1 проверка health endpoint и 6 проверок расчёта цены). Тесты написаны как `unittest.TestCase`, поэтому работают и штатным `unittest`, и `pytest`.
