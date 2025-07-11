from django.contrib.auth.models import User
from django.db import models



class Game(models.Model):
    room_code = models.CharField(max_length=100, unique=True)
    op1 = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='game_as_op1')
    op2 = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='game_as_op2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game {self.room_code}"

