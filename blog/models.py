from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):

    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Post(models.Model):

    title = models.CharField(max_length=70)
    body = models.TextField()

    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()

    excerpt = models.CharField(max_length=200, blank=True)

    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    author = models.ForeignKey(User)
    
    def __str__(self):
        return self.title
    
    # 生成URL
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    class Meta:
        # 指定以后所有返回的文章列表都会自动按照 Meta 中指定的顺序排
        # 序，因此可以删掉视图函数中对文章列表中返回结果进行排序的代码了。
        ordering = ['-created_time', 'title']