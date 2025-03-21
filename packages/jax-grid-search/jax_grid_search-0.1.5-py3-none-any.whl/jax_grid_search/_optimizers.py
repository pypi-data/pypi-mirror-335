from functools import partial
from typing import Any, Callable, NamedTuple, Optional

import jax
import jax.numpy as jnp
import optax
import optax.tree_utils as otu
from jaxtyping import Array, PyTree

from ._progressbar import ProgressBar


class OptimizerState(NamedTuple):
    params: PyTree
    state: PyTree
    updates: PyTree
    update_norm: float
    value: float
    best_val: float
    best_params: PyTree


def _debug_callback(
    id: int,
    arguments: Any,
) -> str:
    update_norm, tol, iter_num, value, max_iters = arguments
    return f"Optimizing {id}... update {update_norm:.0e} => {tol:.0e} at iter {iter_num} value {value:.0e}"


@partial(jax.jit, static_argnums=(1, 2, 3, 5))
def optimize(
    init_params: Array,
    fun: Callable[[Array], Array],
    opt: optax._src.base.GradientTransformationExtraArgs,
    max_iter: int,
    tol: Array,
    progress: Optional[ProgressBar] = None,
    progress_id: int = 0,
    upper_bound: Optional[Array] = None,
    lower_bound: Optional[Array] = None,
    **kwargs: Any,
) -> tuple[Array, OptimizerState]:
    # Define a function that computes both value and gradient of the objective.
    value_and_grad_fun = jax.value_and_grad(fun)

    # Single optimization step.
    def step(carry: OptimizerState) -> OptimizerState:
        value, grad = value_and_grad_fun(carry.params, **kwargs)  # Compute value and gradient
        updates, state = opt.update(grad, carry.state, carry.params, value=carry.value, grad=grad, value_fn=fun, **kwargs)  # Perform update
        update_norm = otu.tree_l2_norm(updates)  # Compute update norm
        params = optax.apply_updates(carry.params, updates)  # Update params
        if upper_bound is not None and lower_bound is not None:
            params = optax.projections.projection_box(params, lower_bound, upper_bound)  # Apply box constraints

        best_params = jax.tree.map(
            lambda x, y: jnp.where(carry.best_val < value, x, y),
            carry.best_params,
            carry.params,
        )
        best_val = jnp.where(carry.best_val < value, carry.best_val, value)

        if progress:
            iter_num = otu.tree_get(carry.state, "count")
            progress.update(progress_id, (update_norm, tol, iter_num, carry.value, max_iter), desc_cb=_debug_callback, total=max_iter)

        return carry._replace(
            params=params,
            state=state,
            updates=updates,
            value=value,
            best_val=best_val,
            best_params=best_params,
            update_norm=update_norm,
        )

    # Stopping condition.
    def continuing_criterion(carry: OptimizerState) -> Any:
        iter_num = otu.tree_get(carry.state, "count")  # Get iteration count from optimizer state
        iter_num = 0 if iter_num is None else iter_num
        update_norm = carry.update_norm
        return (iter_num == 0) | ((iter_num < max_iter) & (update_norm >= tol))

    # Initialize optimizer state.
    init_state = OptimizerState(init_params, opt.init(init_params), init_params, jnp.inf, jnp.inf, jnp.inf, init_params)

    # Run the while loop.
    if progress:
        progress.create_task(progress_id, total=max_iter)
    final_opt_state = jax.lax.while_loop(continuing_criterion, step, init_state)
    if progress:
        progress.finish(progress_id, total=max_iter)

    # Was the last evaluation better than the best?
    best_params = jax.tree.map(
        lambda x, y: jnp.where(final_opt_state.best_val < final_opt_state.value, x, y),
        final_opt_state.best_params,
        final_opt_state.params,
    )
    best_value: float = jnp.where(
        final_opt_state.best_val < final_opt_state.value,
        final_opt_state.best_val,
        final_opt_state.value,
    )  # type: ignore[assignment]
    final_opt_state = final_opt_state._replace(best_params=best_params, best_val=best_value)

    return final_opt_state.best_params, final_opt_state
