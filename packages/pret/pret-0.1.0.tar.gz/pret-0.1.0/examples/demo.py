import numpy as np

from pret.main import run
from pret.render import component, server_only
from pret.ui.react import use_state
from pret.state import proxy, use_tracked
from pret.stubs.allotment import Allotment
# from pret.stubs.metanno_text import TextComponent
from pret.stubs.mui import (
    AppBar,
    Box,
    Button,
    CssBaseline,
    Drawer,
    List,
    ListItem,
    Tab,
    Tabs,
    ThemeProvider,
    Typography,
    create_theme,
)
#from pret.stubs.mui_markdown import MuiMarkdown
from pret.stubs.react import div

#test = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
html = "ok"#test.to_html()
print(html)


@server_only
def get_server_compute():
    return np.mean(np.random.randn(500))


@component
def TabPanel(*children, index=None, value=None):
    data = use_tracked(state)

    server_value, set_server_value = use_state(0)

    async def handle_click(e):
        state["count"] += 1
        set_server_value(await get_server_compute())

    return Box(
        Allotment(
            Allotment(
                div(
                    *(
                        (
                            Typography("Mon titre B", variant="h3"),
                            Button(
                                f"mon bouton: {data['count']}, ma valeur: {server_value}",
                                variant="contained",
                                color="primary" if data["count"] % 2 == 0 else "secondary",
                                disable_ripple=True,
                                on_click=handle_click,
                            ),
                            Button(
                                "survole moi !",
                                variant="contained",
                                color="primary",
                                on_mouse_enter=handle_click,
                            ),
                        )
                        if (value == index)
                        else ()
                    ),
                ),
                div(dangerously_set_inner_html={"__html": html}),
                separator=True,
                vertical=True,
            ),
            # MyText(),
            vertical=False,
            separator=True,
        ),
        # props
        role="tabpanel",
        hidden=index != value,
        id=f"simple-tabpanel-{index}",
        aria_labelledby=f"simple-tab-{index}",
        sx={"height": "100%"},
    )


def MyText(*children, **props):
    return TextComponent(
        text="""Le soir, après avoir mangé sa soupe aux choux noyée d’eau, Charlie allait toujours dans la
chambre de ses quatre grands-parents pour écouter leurs histoires, et pour leur souhaiter
bonne nuit.
Chacun d’eux avait plus de quatre-vingt-dix ans. Ils étaient fripés comme des pruneaux
secs, ossus comme des squelettes et, toute la journée, jusqu’à l’apparition de Charlie, ils se
pelotonnaient dans leur lit, deux de chaque côté, coiffés de bonnets de nuit qui leur tenaient
chaud, passant le temps à ne rien faire. Mais dès qu’ils entendaient la porte s’ouvrir, puis la voix
du petit Charlie qui disait : « Bonsoir, grand-papa Joe et grand-maman Joséphine, bonsoir
grand-papa Georges et grand-maman Georgina », tous les quatre se dressaient dans leur lit,
leurs vieilles figures ridées lui souriaient, illuminées de plaisir – et ils commençaient à lui
raconter des histoires. Car ils aimaient beaucoup le petit garçon. Il était leur seule joie et,
toute la journée, ils attendaient impatiemment l’heure de sa visite. Souvent, ses parents
l’accompagnaient et, debout dans l’encadrement de la porte, ils écoutaient les histoires des
grands-parents ; ainsi, chaque soir, pendant une demi-heure environ, la chambre devenait un
endroit joyeux et toute la famille oubliait la faim et la misère.
Un soir, en venant voir ses grands-parents, Charlie leur dit : « Est-il bien vrai que la
Chocolaterie Wonka est la plus grande du monde ? »""",
        spans=[
            {"begin": 0, "end": 11, "id": "id-1"},
            {"begin": 55, "end": 71, "id": "id-2"},
        ],
        actions={},
        **props,
    )


@component
def View():
    # count, set_count = use_state(0)
    index, set_index = use_state(0)

    def handle_index_change(e, new_index):
        set_index(new_index)

    return Box(
        Box(
            Tabs(
                Tab(
                    label="Item One",
                    aria_controls="simple-tabpanel-0",
                    key="simple-tab-0",
                ),
                Tab(
                    label="Item Two",
                    aria_controls="simple-tabpanel-1",
                    key="simple-tab-1",
                ),
                Tab(
                    label="Item Three",
                    aria_controls="simple-tabpanel-2",
                    key="simple-tab-2",
                ),
                value=index,
                on_change=handle_index_change,
                aria_label="basic tabs example",
            ),
            borderBottom=1,
            borderColor="divider",
        ),
        TabPanel(
            key="tab-panel-0",
            index=0,
            value=index,
        )
        if index == 0
        else None,
        TabPanel(
            key="tab-panel-1",
            index=1,
            value=index,
        )
        if index == 1
        else None,
        TabPanel(
            key="tab-panel-1",
            index=1,
            value=index,
        )
        if index == 2
        else None,
        component="main",
        sx={"p": 3, "flex": 1},
    )


@component
def App():
    theme = create_theme(
        {
            "palette": {
                "primary": {
                    "light": "#ff0000",
                    "dark": "#ff0000",
                    "main": "#ff0000",
                },
                "secondary": {
                    "light": "#00ff00",
                    "dark": "#00ff00",
                    "main": "#00ff00",
                },
            },
            "typography": {
                "fontFamily": ",".join(
                    [
                        "-apple-system",
                        "BlinkMacSystemFont",
                        '"Segoe UI"',
                        "Roboto",
                        '"Helvetica Neue"',
                        "Arial",
                        "sans-serif",
                        '"Apple Color Emoji"',
                        '"Segoe UI Emoji"',
                        '"Segoe UI Symbol"',
                    ]
                ),
            },
        }
    )
    return ThemeProvider(
        CssBaseline(),
        div(
            Drawer(
                List(
                    ListItem(Typography("Drawer", variant="h6")),
#                    ListItem(
#                        MuiMarkdown(
#                            """\
#Metanno est un paquet python pour développer des annotateurs configurables.
#
#> Citation pertinente
#
#```bash
#pret stub @mui/material
#```
#"""
#                        ),
#                        sx={"width": 250},
#                        role="presentation",
#                    ),
                ),
                sx={"width": 250, "display": "block"},
                open=True,
                variant="permanent",
                anchor="left",
            ),
            Box(
                AppBar(
                    Typography("Mon app", variant="h6"),
                    position="sticky",
                    sx={"p": 1},
                ),
                View(),
                sx={
                    "width": "calc(100% - 250px)",
                    "height": "100%",
                    "display": "flex",
                    "flexDirection": "column",
                },
            ),
            style={"display": "flex", "height": "100vh"},
        ),
        theme=theme,
    )


state = proxy(
    {
        "count": 0,
        "value": 0,
    },
    remote_sync=True,
)

if __name__ == "__main__":
    run(App(), bundle="federated")
