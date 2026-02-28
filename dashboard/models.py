from django.db import models
from django.conf import settings

class BusinessInsight(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insights')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight for {self.seller.username} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Business Insights"
