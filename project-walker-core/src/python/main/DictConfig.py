#!/usr/bin/python
# -*- coding: utf-8 -*-


def forObj(obj):
    return DictConfigParser(obj)


class DictConfigParser:

    def __init__(
        self,
        obj,
        isCaseSensitive=True,
        removeChars=None,
        isLongestTokenMatch=False,
        ):

        self.obj = obj
        self.options = []
        self.isCaseSensitive = isCaseSensitive
        self.removeChars = removeChars
        self.isLongestTokenMatch = isLongestTokenMatch

    def addOption(
        self,
        name,
        default=None,
        description=None,
        isList=False,
        ):

        self.options.append(DictOption(name, default, description, isList))

    def parse(self, config):
        for option in self.options:
            val = self.__getVal(option.name, config)
            if not val and option.isRequired():
                raise OptionException('option [{}] isRequired in [{}] but not present'.format(option.name, self.obj))
            elif not val and not option.isRequired():
                val = option.default

            if option.isList and type(val) != list:
                val = [val]

            self.obj.__dict__[option.name] = val

    def __getVal(self, name, config):
        if self.isCaseSensitive and not self.removeChars and not self.isLongestTokenMatch:
            if name in config:
                return config[name]
            else:
                return None
        else:
            val = None
            for (ckey, cval) in config.iteritems():
                key = ckey
                if not self.isCaseSensitive:
                    name = name.lower()
                    key = ckey.lower()

                if self.removeChars:
                    for c in self.removeChars:
                        key = key.replace(c, '')

                if self.isLongestTokenMatch:
                    if name.find(key) == 0:
                        val = config[ckey]
                        break
                else:
                    if key == name:
                        val = config[ckey]
                        break

            return val


class DictOption:

    def __init__(
        self,
        name,
        default,
        description,
        isList,
        ):

        self.name = name
        self.default = default
        self.description = description
        self.isList = isList

    def isRequired(self):
        return self.default == None

    def __str__(self):
        return '{}: {} [{}]'.format(name, description, default)


class OptionException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


