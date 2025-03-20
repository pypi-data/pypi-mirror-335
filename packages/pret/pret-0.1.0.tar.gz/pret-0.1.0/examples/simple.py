from pret import component, proxy, run, use_state, use_tracked
from pret.ui.joy import Checkbox, Input, Stack, Typography

state = proxy(
    {
        "faire à manger": True,
        "faire la vaisselle": False,
    },
    remote_sync=True,
)


@component
def TodoApp():
    todos = use_tracked(state)
    typed, set_typed = use_state("")
    num_remaining = sum(not ok for ok in todos.values())
    plural = "s" if num_remaining > 1 else ""

    def on_key_down(event):
        if event.key == "Enter":
            todos[typed] = False
            set_typed("")

    return Stack(
        *(
            Checkbox(
                label=todo,
                checked=ok,
                on_change=lambda e, t=todo: todos.update({t: e.target.checked}),
            )
            for todo, ok in todos.items()
        ),
        Input(
            value=typed,
            on_change=lambda event: set_typed(event.target.value),
            on_key_down=on_key_down,
            placeholder="Add a todo",
        ),
        Typography(
            f"Number of unfinished todo{plural}: {num_remaining}",
            sx={"minWidth": "230px"},  # just to avoid jittering when it's centered
        ),
        spacing=2,
        sx={"m": 1},
    )


if __name__ == "__main__":
    run(TodoApp())
