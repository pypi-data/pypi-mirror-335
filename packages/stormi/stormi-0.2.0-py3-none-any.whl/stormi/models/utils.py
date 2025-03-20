from typing import Any, Tuple

import diffrax as dfx
import jax
import jax.numpy as jnp


# Define the ODE solver function
def solve_DE(
    ts: Any,
    params: Tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
    drift: Any,
    initial_state: Any,
    t0: float = 0.0,
    t1: float = 1.0,
    diffusion=None,
    bm=None,
    time_step: float = 0.1,
    dense=False,
    max_steps=40000,
    adjoint=dfx.RecursiveCheckpointAdjoint(),
    solver=dfx.Euler(),
) -> Any:
    """
    Solve the coupled transcription-splicing model using an arbitrary function for transcription rates.

    Args:
        ts: Array of time points at which to evaluate the solution.
        params: Tuple containing model parameters (G, beta_g, gamma_g, nn_params, T_ON).
        drift: The model function defining the ODE system.
        diffusion: The model function defining the diffusion term in the ODE system.
        bm: Virtual Brownian tree object for use in the diffusion term.
        initial_state: Initial state vector [u_1, ..., u_G, s_1, ..., s_G].
        time_step: Initial time step for the solver.
        dense: Whether to calculate dense solution and then interpolate to calculate values at each point.
                If False (default), then ts needs to be a sorted array, starting at the smallest time.
        max_steps: Maximal number of steps in numerical solver. Defaults to 4000.
        adjoint: Adjoint method to use for solving. Defaults to RecursiveCheckpointAdjoint.
        solver: Numerical solver to use. Defaults to Euler.

    Returns:
        Solution object returned by `diffeqsolve`.
    """

    # set DE terms
    if diffusion is None:
        terms = dfx.ODETerm(drift)
        t0 = jnp.min(jnp.minimum(ts, params[-1]))
        t1 = jnp.max(ts)
    else:
        terms = dfx.MultiTerm(dfx.ODETerm(drift), dfx.ControlTerm(diffusion, bm))

    if dense == False:
        saveat = dfx.SaveAt(ts=ts)
    else:
        saveat = dfx.SaveAt(dense=dense)

    solution = dfx.diffeqsolve(
        terms=terms,
        solver=solver,
        t0=t0,
        t1=t1,
        dt0=time_step,
        max_steps=max_steps,
        y0=initial_state,
        args=params,  # Pass all necessary parameters including nn_params
        adjoint=adjoint,
        saveat=saveat,
    )

    if dense:
        # Interpolate the solution at each time in `ts`
        def interp_one_time(t):
            return solution.evaluate(t)[..., :2]

        # Vectorize over `ts`
        batched_interp = jax.vmap(interp_one_time)
        return batched_interp(ts)

    else:
        return solution.ys


# Define the time sorting function
def sort_times_over_all_cells(
    times: Any,
) -> Tuple[Any, Any, Any]:
    """
    Generates a sorted time vector from the provided times matrix.

    Args:
        times (jnp.ndarray): Time matrix with shape (num_cells, num_timepoints).

    Returns:
        Tuple of:
            - sorted_flat_times (jnp.ndarray): Unified sorted time vector.
            - sorted_to_original_indices (jnp.ndarray): Indices mapping sorted times back.
            - original_to_sorted_indices (jnp.ndarray): Permutation indices for sorting.
    """
    flat_times = times.flatten()
    original_to_sorted_indices = jnp.argsort(flat_times)
    sorted_flat_times = flat_times[original_to_sorted_indices]

    # To map back, use searchsorted
    sorted_to_original_indices = jnp.searchsorted(sorted_flat_times, times, side="left")

    return (
        sorted_flat_times,
        sorted_to_original_indices,
        original_to_sorted_indices,
    )
