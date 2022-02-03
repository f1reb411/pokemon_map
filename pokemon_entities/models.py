from django.db import models  # noqa F401


class Pokemon(models.Model):
    title_ru = models.CharField('название', max_length=200)
    title_en = models.CharField('название на английском', max_length=200)
    title_jp = models.CharField('название на японском', max_length=200)
    image = models.ImageField('картинка', null=True, blank=True)
    description = models.TextField('описание')
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='предыдущая эволюция',
        related_name='next_evolution',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title_ru


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, verbose_name='покемон', related_name='entities', on_delete=models.CASCADE)
    lat = models.FloatField('широта')
    lon = models.FloatField('долгота')
    appeared_at = models.DateTimeField('появится', null=True, blank=True)
    disappeared_at = models.DateTimeField('исчезнет', null=True, blank=True)
    level = models.IntegerField('уровень', null=True)
    health = models.IntegerField('здоровье', null=True, blank=True)
    strength = models.IntegerField('сила', null=True, blank=True)
    defence = models.IntegerField('защита', null=True, blank=True)
    stamina = models.IntegerField('выносливость', null=True, blank=True)
