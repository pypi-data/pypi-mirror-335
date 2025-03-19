from .._dict import BaseDictionary


class Works:
    video__detail = {**BaseDictionary.works.video__detail}


class Dictionary:
    works = Works()
