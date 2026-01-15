from .resources import icons
from .resources import images
from .resources.compile_icons import svg_path, png_path, ico_path
from .widgets.button import Button
from .widgets.image_box import ImageBox
from .widgets.switch import SwitchControl
from .widgets.tab_widget import TabWidget, TabBar
try:
    from .models.dataframe_model import DataFrameModel
except ImportError:
    # print('For using DataFrameModel you need to install pandas')
    ...
from .layouts.flow_layout import FlowLayout
from .style.palettes import dark, light
from .style.stylesheets import stylesheet
from .designer import run_designer

__version__ = '0.1.0'