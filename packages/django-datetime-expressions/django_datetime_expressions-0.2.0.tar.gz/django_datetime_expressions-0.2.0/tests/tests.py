from datetime import datetime
from typing import Union

from dateutil.relativedelta import relativedelta
from django.db.models import F
from django.test import TestCase

from datetime_expressions import (
    RelativeDay,
    RelativeHour,
    RelativeMinute,
    RelativeMonth,
    RelativeSecond,
    RelativeWeek,
    RelativeYear,
)

from .models import Article


class RelativeExpressionTestCaseMixin:
    expressions: Union[
        RelativeDay,
        RelativeHour,
        RelativeMinute,
        RelativeMonth,
        RelativeSecond,
        RelativeWeek,
        RelativeYear,
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Article.objects.create(date=datetime(2000, 1, 1, 12, 00, 00))

    def test_addition(self):
        date_expression = self.expressions(F("date"), 1)

        article = Article.objects.annotate(
            additional_date=date_expression
        ).first()

        article_calc_datetime = article.date + relativedelta(
            **{date_expression._duration_type: 1}
        )
        self.assertEqual(
            article_calc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            article.additional_date.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def test_subtraction(self):
        date_expression = self.expressions(F("date"), -1)

        article = Article.objects.annotate(
            additional_date=date_expression
        ).first()
        article_calc_datetime = article.date - relativedelta(
            **{date_expression._duration_type: 1}
        )
        self.assertEqual(
            article_calc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            article.additional_date.strftime("%Y-%m-%d %H:%M:%S"),
        )


class TestRelativeYear(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeYear


class TestRelativeMonth(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeMonth


class TestRelativeWeek(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeWeek


class TestRelativeDay(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeDay


class TestRelativeHour(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeHour


class TestRelativeMinute(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeMinute


class TestRelativeSecond(RelativeExpressionTestCaseMixin, TestCase):
    expressions = RelativeSecond
