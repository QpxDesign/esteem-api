import dataclasses
import datetime
import functools
import math
import re
from typing import Optional
import cartopy.crs as ccrs
from graphcast import autoregressive
from graphcast import casting
from graphcast import checkpoint
from graphcast import data_utils
from graphcast import graphcast
from graphcast import normalization
from graphcast import rollout
from graphcast import xarray_jax
from graphcast import xarray_tree
from IPython.display import HTML
import ipywidgets as widgets
import haiku as hk
import jax
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import xarray


def forecast():
    with open(f"./data/models/graphcast_model.npz", "rb") as f:
        ckpt = checkpoint.load(f, graphcast.CheckPoint)
    params = ckpt.params
    state = {}

    model_config = ckpt.model_config
    task_config = ckpt.task_config

    with open(f"./data/tests/source-era5_date-2022-01-01_res-0.25_levels-37_steps-04.nc", "rb") as f:  # source
        example_batch = xarray.load_dataset(f).compute()

    eval_steps = 1  # time (in hours)

    eval_inputs, eval_targets, eval_forcings = data_utils.extract_inputs_targets_forcings(
        example_batch, target_lead_times=slice("6h", f"{eval_steps*6}h"),
        **dataclasses.asdict(task_config))

    ### JITTER FUNCTION ###
    with open("./data/stats/stats_diffs_stddev_by_level.nc", "rb") as f:
        diffs_stddev_by_level = xarray.load_dataset(f).compute()
    with open("./data/stats/stats_mean_by_level.nc", "rb") as f:
        mean_by_level = xarray.load_dataset(f).compute()
    with open("./data/stats/stats_stddev_by_level.nc", "rb") as f:
        stddev_by_level = xarray.load_dataset(f).compute()

    def with_configs(fn):
        return functools.partial(
            fn, model_config=model_config, task_config=task_config)

    def with_params(fn):
        return functools.partial(fn, params=params, state=state)

    def construct_wrapped_graphcast(
            model_config: graphcast.ModelConfig,
            task_config: graphcast.TaskConfig):
        """Constructs and wraps the GraphCast Predictor."""
        predictor = graphcast.GraphCast(model_config, task_config)

        predictor = casting.Bfloat16Cast(predictor)

        predictor = normalization.InputsAndResiduals(
            predictor,
            diffs_stddev_by_level=diffs_stddev_by_level,
            mean_by_level=mean_by_level,
            stddev_by_level=stddev_by_level)

        predictor = autoregressive.Predictor(
            predictor, gradient_checkpointing=True)
        return predictor

    def drop_state(fn):
        return lambda **kw: fn(**kw)[0]

    @hk.transform_with_state
    def run_forward(model_config, task_config, inputs, targets_template, forcings):
        predictor = construct_wrapped_graphcast(model_config, task_config)
        return predictor(inputs, targets_template=targets_template, forcings=forcings)

    run_forward_jitted = drop_state(with_params(jax.jit(with_configs(
        run_forward.apply))))

    ### JITTER FUNCTION (end) ###

    assert model_config.resolution in (0, 360. / eval_inputs.sizes["lon"]), (
        "Model resolution doesn't match the data resolution. You likely want to "
        "re-filter the dataset list, and download the correct data.")

    print("Inputs:  ", eval_inputs.dims.mapping)
    print("Targets: ", eval_targets.dims.mapping)
    print("Forcings:", eval_forcings.dims.mapping)

    predictions = rollout.chunked_prediction(
        run_forward_jitted,
        rng=jax.random.PRNGKey(0),
        inputs=eval_inputs,  # For inputs, GraphCast requires just two sets of data: the state of the weather 6 hours ago, and the current state of the weather. The model then predicts the weather 6 hours in the future. This process can then be rolled forward in 6-hour increments to provide state-of-the-art forecasts up to 10 days in advance.
        targets_template=eval_targets * np.nan,
        forcings=eval_forcings)
    print(predictions)
