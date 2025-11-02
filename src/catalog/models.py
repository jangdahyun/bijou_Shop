from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    depth = models.PositiveSmallIntegerField(default=0)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["depth", "display_order", "name"] # 카테고리 정렬 순서 지정
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        self.depth = self.parent.depth + 1 if self.parent else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
