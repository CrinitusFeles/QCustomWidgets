from .resources import icons
from .resources import images
from .resources.compile_icons import svg_path, png_path
from .widgets.button import Button
from .widgets.image_box import ImageBox
from .widgets.switch import SwitchControl
from .widgets.tab_widget import TabWidget, TabBar
from .models.dataframe_model import DataFrameModel
from .layouts.flow_layout import FlowLayout
from .style.palettes import dark, light
from .style.stylesheets import stylesheet
from .designer import run_designer

__version__ = '0.1.0'