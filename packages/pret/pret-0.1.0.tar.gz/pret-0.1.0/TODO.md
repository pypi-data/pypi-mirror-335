# TODO

- allow remote action calls from the kernel
- 
- [ ] metanno e2e demo
- [ ] handle actions in text/table components. via refs ?
- [ ] handle errors
- [ ] handle no vars args in component
- [ ] inverser args on_mouse_select
- [ ] words with no space -> nowrap
- [ ] only load manager when needed

Problème avec proxy pyodide

- besoin de tout wrapper avec create_proxy
- parfois to_js, parfois pas

Quand faut-il wrapper avec to_js ?

- cela semble vraiment dépendre de la fonction
- si x, set_x = use_state(original): on perd le controle sur la variable originale, 
  mais on la retrouve dans x, donc PyProxy (pas to_js)
- si extend_theme = on perd définitivement le thème, et pas d'interaction avec python: to_js
- par défault, to_js sur les sorties de callback python ? sauf:
	+ use_state
	+ use_tracked
	+ ... toutes les fonctions 