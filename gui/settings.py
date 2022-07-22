# author: Alexander Ritter
# created on: 16/06/2022
# edited by:

# description:
# Contains the structure of the Settings class and functions for loading/saving it

from dataclasses import dataclass
import typing as t
import yaml
import os, shutil
from utils import Renderer, OrbitCam, FrameControl
from gui.render_preview import RenderPreview
from materials.materials import MaterialController
from gui.properties import *

@dataclass
class AspectRatio:
    width: int
    height: int
    
    @classmethod
    def from_dict(cls: t.Type["AspectRatio"], dic: dict):
        return cls(width=dic["width"], height=dic["height"])
    
    def to_dict(self):
        dic = dict()
        dic["width"]  = self.width
        dic["height"] = self.height
        return dic

@dataclass
class Settings():

    auto_updatecheck: bool
    aspect: AspectRatio
    timelimit: float
    
    @classmethod
    def from_dict(cls: t.Type["Settings"], dic: dict):
        return cls(
            auto_updatecheck=dic["auto_updatecheck"],
            aspect = AspectRatio.from_dict(dic["aspect"]),
            timelimit = dic["timelimit"]
        )
    
    def to_dict(self):
        dic = dict()
        dic["auto_updatecheck"] = self.auto_updatecheck
        dic["aspect"]           = self.aspect.to_dict()
        dic["timelimit"]        = self.timelimit
        return dic
    
class Control:
    renderer: Renderer
    preview: RenderPreview
    camera: OrbitCam
    settings: Settings
    material: MaterialController
    frames: FrameControl
    
    def __init__(self, renderer, settings, preview, camera, frames):
        self.renderer = renderer
        self.preview = preview
        self.camera = camera
        self.frames = frames
        self.settings = settings
        if self.settings is None:
            print("Problem loading settings")
            exit()
    
    def re_render(self):
        self.renderer.render(animation=False)
        self.preview.reload()
        print("Updating preview...")
    
    def set_aspect_ratio(self, width: int, height: int) -> None:
        self.settings.aspect.width  = width
        self.settings.aspect.height = height
        self.renderer.set_aspect_ratio(width, height)

    def set_time_limit(self, limit: float):
        assert limit >= 0
        self.settings.timelimit = limit
        self.renderer.set_time_limit(limit)
    
# Parses and returns a Settings object
# May return NoneType, please check outside
def load_settings() -> Settings:
    
    if not os.path.exists(CONFIG_PATH):
        shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
        print(config)
    try:
        settings = Settings.from_dict(config)
        return settings
    except:
        print("Parsing error during config loading, please regenerate it")
   
def save_settings(settings: Settings) -> None:
    print("Saving configuration")
    dic = settings.to_dict()
    with open(CONFIG_PATH, "w") as settingsfile:
        yaml.dump(dic, settingsfile)