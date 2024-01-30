from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator




class ReadingList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,default="Read List")
    created = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField('Post')

    def save(self, *args, **kwargs):
        if not self.pk:
            counter = 1
            while ReadingList.objects.filter(user=self.user, name=self.name).exists():
                self.name = f"{self.name} {counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class Author(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='media/images')
    joined = models.DateTimeField(auto_now_add=True)
    subscribers = models.ManyToManyField(User)

    def __str__(self):
        return self.name




class Post(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    content = models.TextField()
    likes = models.IntegerField(validators = [MinValueValidator(0)])
    comments = models.ManyToManyField('Comment')
    date = models.DateTimeField(auto_now_add=True)
    time_to_read = models.IntegerField()

    def __str__(self):
        return f'{self.author.name}--{self.id}'



class Comment(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    likes = models.IntegerField(validators = [MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}--{self.id}'


