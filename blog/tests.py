from blog.utils import faker
from blog.utils.tests import ManageTestCase
from blog.factory import CategoryFactory, ArticleFactory
from blog.models import Category


class CategoryTestCase(ManageTestCase):
    """
    分类的测试用例
    """

    model_label = 'category'

    def test_create_which_is_not_login(self):
        """不登录的情况下创建数据，因为权限，响应状态码为 403"""
        name = faker.uuid4()
        data = {'data': {'name': name}}
        response = self.create(data, login=False)
        print(response.data)
        self.assertEqual(403, response.status_code)

    def test_create_with_invalid_data(self):
        """使用不合法的数据或者数据结构，进行创建"""
        data = {'name': faker.uuid4()}
        response = self.create(data)
        self.assertEqual(400, response.status_code)

    def test_create(self):
        """创建分类"""

        # 这里使用唯一性的数据，方便验证
        name = faker.uuid4()
        data = {'data': {'name': name}}
        response = self.create(data)

        self.assertEqual(0, response.data['code'])
        self.assertEqual(name, response.data['result']['name'])

    def test_retrieve(self):
        """检索数据"""
        instance = CategoryFactory()
        response = self.retrieve(object_id=instance.id)
        self.assertEqual(response.data['result']['id'], instance.id)

    def test_post_retrieve(self):
        """POST 型检索数据

        前端发起请求，只获取字段 id 对应的数据，其他忽略掉，返回的结果应该是：

        {
            'code': 0,
            'message': '',
            'result': {'id': 13}
        }

        即测试前端希望返回哪些字段就返回哪些字段
        """
        instance = CategoryFactory()

        data = {'fairycloud': {'display_fields': ['id']}}
        response = self.retrieve_enhance(object_id=instance.id, data=data)

        success_dict = {
            'code': 0,
            'message': '',
            'result': {'id': instance.id},
        }
        self.assertDictEqual(success_dict, response.data)

    def test_post_retrieve_with_reverse_m2m_field(self):
        """
        查询分类详情，查询字段包含反向的多对多字段，即此分类对应文章的数据

        查询字段包含了反向字段 article，预期返回的 article 对应
        的数据结构是一个列表
        """
        instance = CategoryFactory()
        article = ArticleFactory()
        article.categories.add(instance)

        data = {'fairycloud': {'display_fields': ['id', {'article': ['id']}]}}
        response = self.retrieve_enhance(object_id=instance.id, data=data)

        success_dict = {
            'code': 0,
            'message': '',
            'result': {'id': instance.id, 'article': [{'id': article.id}]},
        }
        self.assertDictEqual(success_dict, response.data)

    def test_update(self):
        """测试更新"""
        instance = CategoryFactory()

        update_name = faker.uuid4()
        data = {'data': {'name': update_name}}
        response = self.update(object_id=instance.id, data=data)

        success_dict = {
            'code': 0,
            'message': '',
            'result': {
                'id': instance.id,
                'name': update_name,
                'description': instance.description,
            },
        }
        self.assertDictEqual(success_dict, response.data)

    def test_partial_update(self):
        """测试部分更新"""
        instance = CategoryFactory()

        update_name = faker.uuid4()
        data = {'data': {'name': update_name}}
        response = self.update(object_id=instance.id, data=data)

        success_dict = {
            'code': 0,
            'message': '',
            'result': {
                'id': instance.id,
                'name': update_name,
                'description': instance.description,
            },
        }
        self.assertDictEqual(success_dict, response.data)

    def test_patch_enhance(self):
        """PUT 型部分更新"""
        instance = CategoryFactory()

        update_name = faker.uuid4()
        data = {'data': {'name': update_name}}
        response = self.update(object_id=instance.id, data=data)

        success_dict = {
            'code': 0,
            'message': '',
            'result': {
                'id': instance.id,
                'name': update_name,
                'description': instance.description,
            },
        }
        self.assertDictEqual(success_dict, response.data)

    def test_destroy(self):
        """测试删除"""
        instance = CategoryFactory()
        self.destroy(object_id=instance.id)
        self.assertIsNone(Category.objects.filter(id=instance.id).first())
