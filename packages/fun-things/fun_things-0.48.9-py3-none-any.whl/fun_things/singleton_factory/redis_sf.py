from . import SingletonFactory

try:
    from redis import Redis

    _exists = True

except:
    _exists = False


class RedisSF(SingletonFactory["Redis"]):
    def _instantiate(self):
        if not _exists:
            raise ImportError("You don't have `redis` installed!")

        return Redis(
            *self.args,
            **self.kwargs,
        )

    def _destroy(self):
        self.instance.close()

        return True
