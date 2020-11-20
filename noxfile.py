"""
Python 目前支持的范围：'3.6', '3.7', '3.8'


DRF 目前支持的范围： 3.10，3.11

    以下由 DRF 官网摘录

    DRF 3.11 release adds support for Django 3.0.

        - supported Python versions are now: 3.5, 3.6, 3.7, and 3.8.
        - supported Django versions are now: 1.11, 2.0, 2.1, 2.2, and 3.0.
        - This release will be the last to support Python 3.5 or Django 1.11.

    DRF 3.10 release drops support for Python 2.
        - supported Python versions are now: 3.5, 3.6, and 3.7.
        - supported Django versions are now: 1.11, 2.0, 2.1, and 2.2.

Django 目前支持的范围：'2.0', '2.1', '2.2', '3.0', '3.1'

由于 DRF 的支持情况，请使用之前，确认所使用的 DRF 和 Django 版本是否合理
"""

import nox


def tests(session, django, drf):
    """
    执行测试用例

    - 安装依赖
    - 执行单元测试
    """
    session.install(f'django=={django}')
    session.install(f'djangorestframework=={drf}')
    session.install('-r', 'requirements-nox.txt')
    session.run('python', 'manage.py', 'makemigrations')
    session.run('python', 'manage.py', 'migrate')
    session.run('python', 'manage.py', 'test', '--keepdb')


@nox.session(python=['3.6', '3.7', '3.8'])
@nox.parametrize('django', ['2.0', '2.1', '2.2', '3.0', '3.1'])
@nox.parametrize('drf', ['3.11.0'])
def test1(session, django, drf):
    tests(session, django, drf)


@nox.session(python=['3.6', '3.7'])
@nox.parametrize('django', ['2.0', '2.1', '2.2'])
@nox.parametrize('drf', ['3.10.3'])
def test2(session, django, drf):
    tests(session, django, drf)
