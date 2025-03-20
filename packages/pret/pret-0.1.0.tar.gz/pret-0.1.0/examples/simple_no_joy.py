from pret import component, proxy, run, use_state, use_tracked
from pret.ui.react import div, input, p

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

    return div(
        *(
            input(
                label=todo,
                checked=ok,
                type="checkbox",
                on_change=lambda e, t=todo: todos.update({t: e.target.checked}),
                style={"display": "block"},
            )
            for todo, ok in todos.items()
        ),
        input(
            value=typed,
            on_change=lambda event: set_typed(event.target.value),
            on_key_down=on_key_down,
            placeholder="Add a todo",
        ),
        p(f"Number of unfinished todo{plural}: {num_remaining}", level="body-md"),
    )


if __name__ == "__main__":
    run(TodoApp(), bundle="federated")
