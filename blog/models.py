from django.db import models
from django.conf import settings


class Category(models.Model):
    """文章分类"""

    name = models.CharField('名称', max_length=70)
    description = models.CharField('描述', max_length=100, default='')

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'

    def __str__(self):
        return self.name


class Article(models.Model):
    """文章"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.SET_NULL, null=True
    )
    title = models.CharField('标题', max_length=40)
    brief = models.CharField('简介', max_length=50, blank=True, default='')
    cover_image = models.URLField(
        verbose_name='封面图', max_length=1024, blank=True, default=''
    )
    categories = models.ManyToManyField(Category, verbose_name='文章分类')
    content = models.TextField('内容')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ('-update_time',)

    def __str__(self):
        return self.title


class ArticleActivity(models.Model):

    EVENT_READ = 'read'
    EVENT_SHARE = 'share'
    EVENT_VOTE = 'vote'

    EVENTS = ((EVENT_READ, '浏览'), (EVENT_SHARE, '分享'), (EVENT_VOTE, '点赞'))

    article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)
    event = models.CharField('事件', max_length=20, choices=EVENTS, default=EVENT_READ)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='用户',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{}: {}'.format(self.article.title, self.event)

    class Meta:
        verbose_name = '文章数据'
        verbose_name_plural = '文章数据'


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments'
    )
    content = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='用户',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    hidden = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '文章评论'
        verbose_name_plural = '文章评论'

    def __str__(self):
        return '{}: {}'.format(self.article.title, self.id)
