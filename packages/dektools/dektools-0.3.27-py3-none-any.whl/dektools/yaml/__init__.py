import yaml as pyyaml
import yamlloader
from ..serializer.base import SerializerBase
from .tags import StrTag


class Yaml(SerializerBase):
    dump_kwargs = dict(
        allow_unicode=True,
        indent=2,
    )

    def __init__(self, resolvers, encoding=None):
        super().__init__(encoding)
        resolvers = Resolver.clone(resolvers)
        self.loder = resolvers[0]
        self.dumper = resolvers[1]
        self.register_list = []

    def register(self, cls):
        if cls.yaml_tag_multi:
            self.loder.add_multi_constructor(cls.yaml_tag, cls.from_yaml_multi)
        else:
            self.loder.add_constructor(cls.yaml_tag, cls.from_yaml)
        self.dumper.add_multi_representer(cls, cls.to_yaml)
        self.register_list.append(cls)
        return cls

    def reg_batch(self, *cls_list):
        for cls in cls_list:
            self.register(cls)

    def reg_other(self, yml):
        self.reg_batch(*yml.register_list)

    def data_final(self, data):
        for cls in self.register_list:
            data = cls.data_final(data)
        return data

    def _load_file(self, file):
        return self.data_final(pyyaml.load(file, Loader=self.loder))

    def _dump_file(self, obj, file, kwargs):
        pyyaml.dump(obj, file, Dumper=self.dumper, **(self.dump_kwargs | kwargs))


class Resolver:
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    basic = (Loader, Dumper)
    ordereddict = (yamlloader.ordereddict.CLoader, yamlloader.ordereddict.CDumper)

    @classmethod
    def clone(cls, resolvers):
        loader, dumper = resolvers
        return type('loader', (loader,), dict(
            **cls.removed_implicit_resolver(loader, {'tag:yaml.org,2002:timestamp'}),
            yaml_constructors=getattr(loader, 'yaml_constructors', {}).copy(),
            yaml_multi_constructors=getattr(loader, 'yaml_multi_constructors', {}).copy(),
        )), type('dumper', (dumper,), dict(
            yaml_representers=getattr(dumper, 'yaml_representers', {}).copy(),
            yaml_multi_representers=getattr(dumper, 'yaml_multi_representers', {}).copy()
        ))

    @staticmethod
    def removed_implicit_resolver(cls, tag_set):
        # https://stackoverflow.com/questions/34667108/ignore-dates-and-times-while-parsing-yaml/37958106#37958106
        key = 'yaml_implicit_resolvers'
        data = getattr(cls, key, {}).copy()
        for first_letter, mappings in data.items():
            data[first_letter] = [(tag, regexp) for tag, regexp in mappings if tag not in tag_set]
        return {key: data}


yaml = Yaml(resolvers=Resolver.ordereddict)
yaml.reg_batch(StrTag)
