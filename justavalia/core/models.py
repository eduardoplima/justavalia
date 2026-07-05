from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuário customizado.

    Definido já na Fase 0 (mesmo vazio) porque trocar AUTH_USER_MODEL depois da
    primeira migração é um retrabalho custoso no Django. Campos adicionais
    (avaliador CRECI/CNAI, cliente etc.) chegam nas fases que os exigem.
    """

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
