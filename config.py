#-*- encoding: utf-8
import json

class Config:
    @classmethod
    def open(cls, configpath: str):
        with open(configpath, "r") as f:
            js = json.load(f)
        return js
        