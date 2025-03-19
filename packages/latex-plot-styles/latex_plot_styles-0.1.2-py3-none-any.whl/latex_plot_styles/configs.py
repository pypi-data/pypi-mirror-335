from pydantic import BaseModel

class Config(BaseModel):
    use_tex:bool
    font_family:str
    font:str
    axes_labelsize:int
    font_size:int
    legend_fontsize:int
    xtick_labelsize:int
    ytick_labelsize:int
    stylesheet_name:str
    width:float
    height:float
    color_palette:str

THESIS_CONFIG = Config(
    use_tex=True,
    font_family="serif",
    font="Palatino",
    axes_labelsize=8,
    font_size=8,
    legend_fontsize=8,
    xtick_labelsize=8,
    ytick_labelsize=8,
    stylesheet_name="seaborn-v0_8",
    width=455.24411,
    height=654.41351,
    color_palette="deep",
)