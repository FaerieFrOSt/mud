class   Factory:
    def __init__(self, klass):
        self.objects = []
        self.klass = klass

    def get(self, *args, **kwargs):
        try:
            key, value = kwargs.popitem()
            for i in self.objects:
                if getattr(i, key) == value:
                    return i
        except KeyError:
            pass
        if not args:
            return None
        p = self.klass(*args)
        self.objects.append(p)
        return p

    def delete(self, Object):
        self.objects.remove(Object)

    def map(self, function):
        ret = []
        for i in self.objects:
            ret.append(function(i))
        return ret
