from rest_framework.test import APITestCase

from blog.factory import UserFactory


class BaseTestCase(APITestCase):
    def create_user(self, is_staff=False):
        return UserFactory(is_staff=is_staff)

    def login(self, user=None):
        if not user:
            assert hasattr(
                self, 'user'
            ), 'TestCase must create a user before call login method'

            user = self.user

        self.client.force_authenticate(self.user)


class ManageTestCase(BaseTestCase):
    """管理端基类"""

    app_label = 'blog'

    def get_url(self, function_slug, object_id=None):
        pre_url = f'/fairycloud/manage/{self.app_label}/{self.model_label}'

        if function_slug == 'retrieve_enhance':
            return f'{pre_url}/{object_id}/retrieve/'

        if function_slug == 'retrieve_mine':
            return f'{pre_url}/{object_id}/retrieve/mine/'

        if function_slug == 'list_enhance':
            return f'{pre_url}/list/'

        if function_slug == 'list_mine':
            return f'{pre_url}/list/mine/'

        if function_slug in ['list', 'create']:
            return f'{pre_url}/'
        if function_slug in ['retrieve', 'destroy', 'update', 'partial_update']:
            return f'{pre_url}/{object_id}/'

        if function_slug == 'patch_enhance':
            return f'{pre_url}/{object_id}/patch/'

        if function_slug == 'cloudfunc':
            return f'{pre_url}/cloudfunc/'

        if function_slug == 'batch_process':
            return f'{pre_url}/batch/'

    def create(self, data=None, object_id=None, login=True):
        """创建动作"""
        if login:
            self.login()
        return self.client.post(self.get_url('create'), data=data, format='json')

    def retrieve(self, data=None, object_id=None, login=True):
        """检索"""
        if login:
            self.login()
        return self.client.get(self.get_url('retrieve', object_id), format='json')

    def retrieve_enhance(self, data=None, object_id=None, login=True):
        """post 型检索"""
        if login:
            self.login()
        return self.client.post(
            self.get_url('retrieve_enhance', object_id), data=data, format='json'
        )

    def update(self, data=None, object_id=None, login=True):
        """更新"""
        if login:
            self.login()
        return self.client.put(
            self.get_url('update', object_id), data=data, format='json'
        )

    def partial_update(self, data=None, object_id=None, login=True):
        """部分更新"""
        if login:
            self.login()
        return self.client.patch(
            self.get_url('partial_update', object_id), data=data, format='json'
        )

    def patch_enhance(self, data=None, object_id=None, login=True):
        """PUT 型的部分更新"""
        if login:
            self.login()
        return self.client.put(
            self.get_url('patch_enhance', object_id), data=data, format='json'
        )

    def destroy(self, data=None, object_id=None, login=True):
        """删除操作"""
        if login:
            self.login()
        return self.client.delete(self.get_url('destroy', object_id), format='json')

    def setUp(self):
        self.user = self.create_user(is_staff=True)
