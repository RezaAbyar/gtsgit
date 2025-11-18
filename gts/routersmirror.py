import random
from django.conf import settings

class ReplicationRouter:
    def db_for_read(self, model, **hints):
        """
        Randomly pick a database to read from
        """
        return random.choice([key for key in settings.DATABASES])

    def db_for_write(self, model, **hints):
        """
        Always send write queries to the master database.
        """
        return 'default';

    def allow_relation(self, obj1, obj2, **hints):
        """
        This isn't really applicable for this use-case.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migration operations on the master database, just in case.
        """
        if db == 'default':
            return True
        return None