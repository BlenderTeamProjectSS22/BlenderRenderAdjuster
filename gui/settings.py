# author: Alexander Ritter
# created on: 16/06/2022
# edited by:

# description:
# Contains the structure of the Settings class and functions for loading/saving it

from dataclasses import dataclass
import typing as t
import yaml
from utils import Renderer, OrbitCam
from gui.render_preview import RenderPreview

@dataclass
class AspectRatio:
    width: int
    height: int
    
    @classmethod
    def from_dict(cls: t.Type["AspectRatio"], dic: dict):
        return cls(width=dic["width"], height=dic["height"])

@dataclass
class Settings():

    renderer: Renderer
    auto_updatecheck: bool
    aspect: AspectRatio
    
    @classmethod
    def from_dict(cls: t.Type["Settings"], renderer, dic: dict):
        return cls(
            renderer=renderer,
            auto_updatecheck=dic["auto_updatecheck"],
            aspect = AspectRatio.from_dict(dic["aspect"])
        )
    
    def set_aspect_ratio(self, width: int, height: int) -> None:
        self.aspect.width  = width
        self.aspect.height = height
        # TODO Change the aspect ratio of the camera in here as well
        self.renderer.set_aspect_ratio(width, height)


    
class Control:
    renderer: Renderer
    preview: RenderPreview
    camera: OrbitCam
    settings: Settings
    
    def __init__(self, renderer, preview, camera):
        self.renderer = renderer
        self.preview = preview
        self.camera = camera
        self.settings = self.load_settings()
        if self.settings is None:
            print("Problem loading settings")
            exit()
    
    def re_render(self):
        self.renderer.render()
        self.preview.reload()
        print("Updating preview...")
    
    # Parses and returns a Settings object
    # May return NoneType, please check outside
    def load_settings(self) -> Settings:
        with open("assets/settings.yaml", "r") as f:
            config = yaml.safe_load(f)
            print(config)
        try:
            settings = Settings.from_dict(self.renderer, config)
            return settings
        except:
            print("Parsing error during config loading, please regenerate it")
       
    def save_settings(self, settings: Settings) -> None:
        print("Saving configuration")
        pass