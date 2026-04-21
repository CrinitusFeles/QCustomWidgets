from .resources import icons  # noqa: F401
from .resources import images  # noqa: F401
from .resources.compile_icons import svg_path, png_path, ico_path  # noqa: F401
from .widgets.button import Button  # noqa: F401
from .widgets.image_box import ImageBox  # noqa: F401
from .widgets.switch import SwitchControl  # noqa: F401
from .widgets.tab_widget import TabWidget, TabBar  # noqa: F401
from .widgets.spin_box import SpinBox  # noqa: F401
try:
    from .models.df_table import DataFrameTable  # noqa: F401
except ImportError:
    # print('For using DataFrameModel you need to install pandas')
    ...
from .layouts.flow_layout import FlowLayout  # noqa: F401
from .style.palettes import dark, light  # noqa: F401
from .style.stylesheets import stylesheet  # noqa: F401
from .designer import run_designer  # noqa: F401

__version__ = '0.1.0'