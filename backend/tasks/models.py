from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    estimated_hours = models.IntegerField(validators=[MinValueValidator(0)])
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Importance level from 1 (low) to 10 (critical)"
    )
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs this task depends on"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title




