from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create_user(self, email, password, manager, admin, **extra_fields):
        if not email:
            raise ValueError('user must have email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
              email=email,
              manager=manager,
              active=True,
              admin=admin,
              last_login=now,
              created=now,
              **extra_fields)
        if password:
            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        user = self._create_user(email, password, **extra_fields)
        user.save(using=self._db)
        return user
