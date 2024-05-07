# -*- coding: utf-8 -*-
import yaml


class Config:
    def __init__(self, profile):
        f = open('config.main.yaml')
        config = yaml.load(f.read())
        self.data = config
        self.data['mode'] = profile
        if profile != 'default':
            if config['overwrite profiles'][profile]:
                for key in config['overwrite profiles'][profile].keys():
                    self.data[key] = config['overwrite profiles'][profile][key]
