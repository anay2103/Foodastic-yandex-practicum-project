from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    pass


class Follow(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='follower')
    following = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique follow'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='prevent self-follow'
            ),
        ]
