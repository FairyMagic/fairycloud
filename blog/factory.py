from django.contrib.auth import get_user_model
from blog.utils import factory
from blog.models import Category, Article

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):

    username = factory.Faker('uuid4')
    is_staff = True

    class Meta:
        model = User


class CategoryFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('uuid4')
    description = factory.Faker('uuid4')

    class Meta:
        model = Category


class ArticleFactory(factory.django.DjangoModelFactory):

    title = factory.Faker('name')
    brief = factory.Faker('uuid4')
    cover_image = factory.Faker('uri')
    content = factory.Faker('paragraph')
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Article
