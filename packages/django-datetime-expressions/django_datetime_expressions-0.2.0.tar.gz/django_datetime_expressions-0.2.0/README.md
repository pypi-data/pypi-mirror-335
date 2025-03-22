# django-datetime-expressions

`django-datetime-expressions` provides custom expressions for Django ORM to simplify datetime operations. It allows relative additions and subtractions to datetime fields.

**[日本語版 (Japanese Version)](README_JP.md)**

## Features

- Perform relative operations on datetime fields (e.g., add/subtract days, weeks, months, years)
- Supports multiple database engines (MySQL, SQLite, Oracle)
- Extract epoch time using `EXTRACT`

## Installation

```bash
pip install django-datetime-expressions
```

## Usage

Below is an example of using `RelativeDay` to manipulate dates.

```python
from datetime import datetime
from django.db.models import F
from datetime_expressions import RelativeDay

# Example: Add 5 days to the current date
queryset = MyModel.objects.annotate(new_date=RelativeDay(F('date_field'), 5))
```

### Supported Relative Operations

| Class Name        | Description         | Unit       |
|-------------------|---------------------|------------|
| `RelativeDay`     | Add/Subtract days   | Days       |
| `RelativeWeek`    | Add/Subtract weeks  | 7-day units|
| `RelativeMonth`   | Add/Subtract months | Months     |
| `RelativeYear`    | Add/Subtract years  | Years      |
| `RelativeHour`    | Add/Subtract hours  | Hours      |
| `RelativeMinute`  | Add/Subtract minutes| Minutes    |
| `RelativeSecond`  | Add/Subtract seconds| Seconds    |

### Extracting Epoch Time

Use the `Epoch` class to extract epoch time (seconds since January 1, 1970) from a datetime field.

```python
from datetime_expressions import Epoch

queryset = MyModel.objects.annotate(epoch_time=Epoch(F('date_field')))
```

## Supported Databases

- MySQL
- SQLite
- Oracle

## Contribution

Bug reports and feature requests are welcome on [GitHub Issues](https://github.com/towan912/django-datetime-expressions/issues). Pull requests are also appreciated!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.