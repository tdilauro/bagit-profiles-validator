import copy
import json
import requests


class Profile(object):
    _top_level_properties = ["BagIt-Profile-Info", "Bag-Info", "Accept-BagIt-Version",
                             "Manifests-Required", "Manifests-Allowed",
                             "Allow-Fetch.txt", "Serialization", "Accept-Serialization",
                             "Tag-Manifests-Required", "Tag-Manifests-Allowed",
                             "Tag-Files-Required", "Tag-Files-Allowed"]
    _profile_info_uri_property = "BagIt-Profile-Identifier"
    _profile_info_version_property = "BagIt-Profile-Version"

    def __init__(self, profile_uri=None, profile_version=None, **kwargs):
        self.validated = False

        properties = {k: v for k, v in kwargs.items() if k in self._top_level_properties}
        options = {k: v for k, v in kwargs.items() if k not in self._top_level_properties}

        self.source = options.pop("source", None)
        self.options = options

        profile_info = properties.get("BagIt-Profile-Info", {})
        if profile_version is None:
            profile_version = profile_info.get(self._profile_info_version_property, None)
        if profile_version is None:
            self.profile_version_info = (1, 1, 0)
        else:
            self.profile_version_info = tuple(int(i) for i in profile_version.split("."))
        if profile_uri is None:
            profile_uri = properties.get("BagIt-Profile-Info", {}).get(self._profile_info_uri_property, None)
        self.profile_uri = profile_uri

        self.options = options
        self._properties = properties

    def __getitem__(self, item):
        if item not in self._top_level_properties:
            print("*** Attribute error for: '{}'".format(item))
            raise AttributeError
        return self._properties[item]

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setitem__(self, key, value):
        if key not in self._top_level_properties:
            raise AttributeError
        self._properties[key] = value

    def __setattr__(self, key, value):
        if key not in self._top_level_properties:
            self.__dict__[key] = value
        else:
            self.__setitem__(key, value)

    def as_dict(self):
        return copy.deepcopy(self._properties)

    def as_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def from_json(cls, json_string, **kwargs):
        obj = json.loads(json_string)
        return cls._factory_helper(obj, kwargs)

    @classmethod
    def from_file(cls, json_file, **kwargs):
        with open(json_file, 'r') as f:
            obj = json.load(f)
        kwargs['source'] = json_file
        return cls._factory_helper(obj, kwargs)

    @classmethod
    def from_url(cls, json_url, **kwargs):
        response = requests.get(json_url)
        obj = response.json()
        kwargs['source'] = json_url
        return cls._factory_helper(obj, kwargs)

    @classmethod
    def _factory_helper(cls, obj, kwargs):
        obj.update(kwargs)
        return cls(**obj)

    def __iter__(self):
        return iter(self._properties)

    def __len__(self):
        return len(self._properties)
