from django.db import models



class Author(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='media/images')

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    content = models.TextField()
    likes = models.IntegerField()
    comments = models.ManyToManyField('Comment')

    def __str__(self):
        return f'{self.author.name}--{self.id}'


class Comment(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f'{self.author.name}--{self.id}'
