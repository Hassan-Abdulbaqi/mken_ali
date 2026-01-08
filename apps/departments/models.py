from django.db import models


class Branch(models.Model):
    """Branch (الفرع) model."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='اسم الفرع'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'فرع'
        verbose_name_plural = 'الفروع'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Department (الشعبة) model."""
    
    name = models.CharField(
        max_length=100,
        verbose_name='اسم الشعبة'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='الفرع',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'شعبة'
        verbose_name_plural = 'الشعب'
        ordering = ['branch__name', 'name']
        unique_together = ['name', 'branch']
    
    def __str__(self):
        if self.branch:
            return f'{self.name} - {self.branch.name}'
        return self.name
