from rest_framework import fields


class CharIntegerField(fields.IntegerField):
    """字符整型字段"""

    def to_representation(self, value):
        return f'{value}'
