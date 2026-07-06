import random
from enum import Enum

import nevu_ui as ui
import pygame  # pygame-ce
import pyray as rl
from nevu_ui import ElementSwitcher
from nevu_ui import animations as anims
from nevu_ui.core.annotations import VERSION

rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
pygame.init()


class AppState(Enum):
    MainMenu = 0
    WidgetsShowcase = 1
    LayoutShowcase = 2
    AnimationsShowcase = 3


class App(ui.Manager):
    def __init__(self):
        # window = ui.InitializedWindow.from_pygame(
        #    pygame.display.set_mode((900, 600), flags=pygame.RESIZABLE),
        #    title="showcase",
        #    ratio=ui.NvVector2(9, 6),
        # )
        # you can use this window instead
        window = ui.Window(
            (900, 600),
            title="showcase",
            backend=ui.Backend.Pygame,
            resizable=True,
            ratio=ui.NvVector2(9, 6),
        )

        self.state = AppState.MainMenu

        self.style = ui.Style(
            border_radius=25,
            colortheme=ui.ColorThemeLibrary.github_dark,
            font_name="assets/vk_font.ttf",
        )

        ui.nevu_object_globals.modify(
            size=(ui.vw % 25, ui.vh % 9),
            style=self.style,
        )

        self.menu = ui.Menu(
            window=window,
            size=ui.fill_all,
            style=ui.Style(
                bg_image="assets/bg.png",
                border_width=0,
            ),
        )

        super().__init__(window, self.menu)
        self.goto_main_menu()
        self.fps = 120

    def change_showcase_item(self, item):
        layout: ui.Grid = self.menu.layout
        oldwidget = layout.get_item(2, 3)
        layout.kill_item(oldwidget)
        layout.add_item(item(), 2, 3)
        current_label = layout.get_item(3, 6)
        element_switcher: ElementSwitcher = layout.get_item(2, 6)
        current_label.text = f"Current: {element_switcher.current_index + 1}/{len(element_switcher.elements)}"

    def create_showgrid(
        self, items: dict[str, ui.NevuObject], first_item: ui.NevuObject, title: str
    ):
        self.menu.layout.kill()

        anim_manager = anims.AnimationManager()
        anim_manager.add_start_animation(
            ui.AnimationType.Position,
            anims.Vector2Animation(
                start=(0, 200), end=(0, 0), time=2, easing_func=anims.spring()
            ),
        )
        layout = ui.Grid(
            size=(ui.vw % 100, ui.vh % 100),
            style=self.style,
            x=3,
            y=6,
            content={
                (2, 3): first_item,
                (2, 6): ui.ElementSwitcher(
                    elements=[item for item in items.keys()],
                    anim_manager=anim_manager,
                    words_indent=True,
                    size=(ui.vw % 45, ui.vh % 12),
                    button_padding=0,
                    subtheme_role=ui.SubThemeRole.PRIMARY,
                    on_content_change=lambda name, id: (
                        self.change_showcase_item(items[name]),
                    ),
                ),
                (1, 6): ui.Label(
                    f"Total: {len(items)}",
                    size=(ui.vw % 25, ui.vh % 5),
                    draw_content=False,
                    draw_borders=False,
                ),
                (3, 6): ui.Label(
                    f"Current: 1/{len(items)}",
                    size=(ui.vw % 25, ui.vh % 5),
                    draw_content=False,
                    draw_borders=False,
                ),
            },
        )
        exit_btn = ui.Button(
            lambda: self.goto_main_menu(),
            "X",
            style=self.style(br=5),
            throw_errors=True,
            size=(ui.vh % 5, ui.vh % 5),
            subtheme_role=ui.SubThemeRole.ERROR,
            single_instance=True,
        )
        desc_lbl = ui.Label(
            title,
            size=(ui.vw % 25, ui.vh % 5),
            draw_borders=False,
            draw_content=False,
            style=self.style(align_x=ui.Align.LEFT),
            single_instance=True,
            z=-999,
        )
        desc_lbl.coordinates = ui.NvVector2(70, 10)
        layout.add_floating_item(desc_lbl)
        exit_btn.coordinates = ui.NvVector2(10, 10)
        layout.add_floating_item(exit_btn)
        self.menu.layout = layout

    def goto_main_menu(self):
        self.state = AppState.MainMenu
        if self.menu.layout:
            self.menu.layout.kill()
        label_animations = anims.AnimationManager()
        label_animations.add_start_animation(
            ui.AnimationType.Position,
            anims.Vector2Animation(
                start=(-700, 0), end=(0, 0), time=2, easing_func=anims.spring()
            ),
        )
        label_animations.transition_time = 0.0001
        label_animations.add_continuous_animation(
            ui.AnimationType.Position,
            anims.Vector2Animation((0, 0), (0, -40), 3, anims.smootherstep),
        )
        with ui.nevu_object_globals.modify_temp(
            subtheme_role=ui.SubThemeRole.PRIMARY,
        ):
            layout = ui.Grid(
                size=ui.fill_all,
                x=6,
                y=5,
                content={
                    (2, 4): ui.Widget(
                        size=(ui.fillw % 40, ui.fillw % 10),
                        style=self.style(bg_image="assets/title.png", br=0, bw=0),
                        inverted=True,
                        animation_manager=label_animations,
                    ),
                    (2, 2): ui.Widget(
                        size=(ui.fillw % 30, ui.fillw % 30),
                        style=self.style(bg_image="assets/logo.png"),
                        draw_borders=False,
                    ),
                    (2, 5): ui.Label(
                        f"nevu-ui v{VERSION}",
                        style=self.style,
                        size=(ui.fillw % 25, ui.fillh % 5),
                        draw_borders=False,
                        draw_content=False,
                    ),
                    (5, 3): ui.Panel(
                        size=(ui.fillw % 30, ui.fillh % 60),
                        bg_widget=ui.Widget(
                            style=self.style,
                            bg_variant=True,
                            draw_borders=False,
                            subtheme_role=ui.SubThemeRole.PRIMARY,
                        ),
                        slot=ui.StackColumn(
                            spacing=30,
                            content=[
                                (
                                    ui.Align.LEFT,
                                    ui.Button(
                                        self.goto_widgets_showcase_layout,
                                        "Widgets",
                                        style=self.style,
                                        id="b1",
                                        subtheme_role=ui.SubThemeRole.PRIMARY,
                                    ),
                                ),
                                (
                                    ui.Align.LEFT,
                                    ui.Button(
                                        self.goto_layouts_showcase_layout,
                                        "Layouts",
                                        style=self.style,
                                        id="b2",
                                        subtheme_role=ui.SubThemeRole.PRIMARY,
                                    ),
                                ),
                                (
                                    ui.Align.LEFT,
                                    ui.Button(
                                        self.goto_animations_showcase_layout,
                                        "Animations",
                                        style=self.style,
                                        id="b3",
                                        subtheme_role=ui.SubThemeRole.PRIMARY,
                                        throw_errors=True,
                                    ),
                                ),
                            ],
                        ),
                    ),
                },
            )
        self.menu.layout = layout

    def goto_widgets_showcase_layout(self):
        self.state = AppState.WidgetsShowcase
        ui.nevu_object_globals.modify(
            style=self.style(colortheme=ui.ColorThemeLibrary.github_dark)
        )
        widgets = {
            "Button": lambda: ui.Button(lambda: print("Clicked!"), "Button"),
            "Label": lambda: ui.Label("Hello, World!"),
            "Widget": lambda: ui.Widget(),
            "ElementSwitcher": lambda: ui.ElementSwitcher(
                elements=["first", "second", "third", "fourth"]
            ),
            "Slider": lambda: ui.Slider(),
            "Switch": lambda: ui.Switch(
                size=(ui.vw % 15, ui.vh % 12),
                style=self.style(colortheme=ui.ColorThemeLibrary.github_dark, br=999),
            ),
            "Input": lambda: ui.Input(
                placeholder="placeholder",
                multiple=True,
                size=(ui.vw % 30, ui.vh % 20),
            ),
        }
        self.create_showgrid(
            widgets, ui.Button(lambda: print("Clicked!"), "Button"), "Widgets Showcase"
        )

    def goto_layouts_showcase_layout(self):
        self.state = AppState.LayoutShowcase
        ui.nevu_object_globals.modify(
            style=self.style(colortheme=ui.ColorThemeLibrary.github_dark)
        )
        size = (ui.vw % 70, ui.vh % 70)
        borders = ui.BorderConfig(
            name="Borders",
            width=1,
            color=ui.Color.Red,
            font="assets/vk_font.ttf",
        )

        stub = ui.Button(
            lambda: print("Clicked!"), "Stub", size=(ui.vw % 10, ui.vw % 10)
        )

        layouts = {
            "Grid": lambda: ui.Grid(
                size=size,
                x=3,
                y=3,
                borders=borders,
                content={
                    (1, 1): stub,
                    (2, 1): stub,
                    (3, 1): stub,
                    (1, 2): stub,
                    (2, 2): stub,
                    (3, 2): stub,
                    (1, 3): stub,
                    (2, 3): stub,
                    (3, 3): stub,
                },
            ),
            "Row": lambda: ui.Row(
                size=size,
                x=3,
                borders=borders,
                content={1: stub, 2: stub, 3: stub},
            ),
            "Column": lambda: ui.Column(
                size=size,
                y=3,
                borders=borders,
                content={1: stub, 2: stub, 3: stub},
            ),
            "StackRow": lambda: ui.StackRow(
                borders=borders,
                content=[(ui.Align.CENTER, stub) for _ in range(7)],
            ),
            "StackColumn": lambda: ui.StackColumn(
                borders=borders,
                content=[(ui.Align.CENTER, stub) for _ in range(5)],
            ),
            "ScrollableRow": lambda: ui.ScrollableRow(
                size=size,
                borders=borders,
                content=[(ui.Align.CENTER, stub) for _ in range(20)],
            ),
            "ScrollableColumn": lambda: ui.ScrollableColumn(
                size=size,
                borders=borders,
                content=[(ui.Align.CENTER, stub) for _ in range(20)],
            ),
            "Panel": lambda: ui.Panel(
                size=size,
                borders=borders,
                slot=stub,
            ),
            "ColorPicker": lambda: ui.ColorPicker(
                title="Color Picker",
                borders=borders,
                input_style=self.style(br=5),
                label_style=self.style(br=30),
            ),
        }
        self.create_showgrid(layouts, layouts["Grid"](), "Layouts Showcase")

    def create_pos_anim_manager(self, func, time):
        anim_manager = anims.AnimationManager()
        rnd = random.randint(0, 1)
        start = ui.NvVector2(-150, 0) if rnd == 0 else ui.NvVector2(0, -150)
        end = ui.NvVector2(150, 0) if rnd == 0 else ui.NvVector2(0, 150)
        anim_manager.add_continuous_animation(
            ui.AnimationType.Position,
            anims.Vector2Animation(
                start=start,
                end=end,
                time=2,
                easing_func=func,
            ),
        )

        return anim_manager

    def _get_random_subtheme(self):
        return random.choice(
            [
                ui.SubThemeRole.PRIMARY,
                ui.SubThemeRole.SECONDARY,
                ui.SubThemeRole.TERTIARY,
                ui.SubThemeRole.ERROR,
            ]
        )

    def _get_random_colortheme(self):
        return random.choice(
            [
                ui.ColorThemeLibrary.github_dark,
                ui.ColorThemeLibrary.gruvbox_dark,
                ui.ColorThemeLibrary.gruvbox_light,
                ui.ColorThemeLibrary.material3_dark,
                ui.ColorThemeLibrary.ocean_light,
                ui.ColorThemeLibrary.synthwave_dark,
                ui.ColorThemeLibrary.catppuccin_latte,
                ui.ColorThemeLibrary.catppuccin_mocha,
            ]
        )

    def goto_animations_showcase_layout(self):
        self.state = AppState.AnimationsShowcase
        crp = self.create_pos_anim_manager
        ui.nevu_object_globals.modify(
            style=self.style(colortheme=ui.ColorThemeLibrary.github_dark)
        )
        animations = {
            "Shake": crp(anims.shake_easing(), 5),
            "Bounce": crp(anims.ease_out_bounce, 5),
            "Linear": crp(anims.linear, 5),
            "Steps(5)": crp(anims.steps(5), 5),
            "Steps(10)": crp(anims.steps(10), 5),
            "Spring": crp(anims.spring(), 5),
            "Smooth Step": crp(anims.smoothstep, 5),
            "Smoother Step": crp(anims.smootherstep, 5),
            "Cubic Bezier (custom)": crp(anims.cubic_bezier(0.1, 0.9, 0.5, 0.0001), 5),
            "Ease In": crp(anims.ease_out_quad, 5),
            "Ease Out": crp(anims.ease_in_quad, 5),
            "Ease In Out": crp(anims.ease_in_out_quad, 5),
            "Ease In Expo": crp(anims.ease_in_expo, 5),
            "Ease Out Expo": crp(anims.ease_out_expo, 5),
            "Ease In Circ": crp(anims.ease_in_circ, 5),
            "Ease Out Circ": crp(anims.ease_out_circ, 5),
            "Ease In Out Circ": crp(anims.ease_in_out_circ, 5),
            "Ease In Out Expo": crp(anims.ease_in_out_expo, 5),
            "Ease In Back": crp(anims.ease_in_back, 5),
            "Ease Out Back": crp(anims.ease_out_back, 5),
            "Ease In Out Back": crp(anims.ease_in_out_back, 5),
            "Ease In Sine": crp(anims.ease_in_sine, 5),
            "Ease Out Sine": crp(anims.ease_out_sine, 5),
            "Ease In Out Sine": crp(anims.ease_in_out_sine, 5),
            "Ease In Cubic": crp(anims.ease_in_cubic, 5),
            "Ease Out Cubic": crp(anims.ease_out_cubic, 5),
            "Ease In Out Cubic": crp(anims.ease_in_out_cubic, 5),
            "Elastic In": crp(anims.ease_in_elastic, 5),
            "Elastic Out": crp(anims.ease_out_elastic, 5),
        }
        dict = {
            name: lambda anim=anim, text=name: ui.Label(
                text=text,
                anim_manager=anim,
                subtheme_role=self._get_random_subtheme(),
                inverted=bool(random.randint(0, 1)),
                bg_variant=bool(random.randint(0, 1)),
                style=self.style(colortheme=self._get_random_colortheme()),
            )
            for name, anim in animations.items()
        }
        self.create_showgrid(dict, dict["Shake"](), "Animations Showcase")

    def on_draw(self):
        self.window.draw_overlay()  # if you want to see layout borders uncomment this


if __name__ == "__main__":
    app = App()
    app.run()
