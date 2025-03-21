class Manager:
    def __init__(self, interaction, model=None):
        self._interaction = interaction
        self._model = model

    def __get__(self, instance, owner):
        if instance is None:
            self._model = owner
            return self
        raise AttributeError("Cant use with instance")

    def __set__(self, instance, value):
        raise TypeError()

    async def create(self, data=None, **kwargs):
        return self._model(data=await self._interaction.create(data=data or kwargs))

    async def update(self, object_id, data=None, **kwargs):
        return await self._interaction.update(object_id=object_id, data=data or kwargs)

    async def get(self, object_id=None, query=None):
        if object_id is not None:
            return self._model(data=await self._interaction.get(object_id, include=self._model._get_embedded_fields()))
        return next(await self.filter(query=query))

    async def filter(self, *args, **kwargs):
        async for data in self._interaction.get_all(*args, include=self._model._get_embedded_fields(), **kwargs):
            yield self._model(data=data)

    def all(self):
        return self.filter()
