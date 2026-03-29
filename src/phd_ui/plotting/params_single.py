from phd_ui.plotting.params_double import params_double


params_single = params_double.copy()
params_single.update({
    "figure.figsize": (3.5, 2.5),
})