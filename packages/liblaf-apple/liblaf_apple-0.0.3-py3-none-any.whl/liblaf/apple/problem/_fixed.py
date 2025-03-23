from typing import overload, override

import attrs
import jax
import numpy as np
from jaxtyping import Bool, Float, PyTree

from liblaf import apple


@apple.register_dataclass()
@attrs.define(kw_only=True, on_setattr=attrs.setters.convert)
class Fixed(apple.AbstractPhysicsProblem):
    name: str = attrs.field(default="fixed", metadata={"static": True})
    problem: apple.AbstractPhysicsProblem = attrs.field()
    fixed_mask: Bool[np.ndarray, " D"] = attrs.field(metadata={"static": True})
    fixed_values: Float[jax.Array, " D"] = attrs.field()

    @property
    def free_mask(self) -> Bool[np.ndarray, " D"]:
        return ~self.fixed_mask

    @property
    def n_dof(self) -> int:
        return self.problem.n_dof - self.n_fixed

    @property
    def n_fixed(self) -> int:
        return np.count_nonzero(self.fixed_mask)

    def fill(self, u: PyTree, q: PyTree | None = None) -> PyTree:
        u_flat: Float[jax.Array, " DoF"] = self.ravel_u(u)
        u_flat: Float[jax.Array, " D"] = self.fill_flat(u_flat, q)
        u: PyTree = self.problem.unravel_u(u_flat)
        return u

    def fill_flat(
        self, u_flat: Float[jax.Array, " D"], q: PyTree | None = None
    ) -> Float[jax.Array, " D"]:
        fixed_values: Float[jax.Array, " D"] = self.get_param("fixed_values", q)
        u_filled: Float[jax.Array, " D"] = fixed_values.at[self.free_mask].set(u_flat)
        return u_filled

    @apple.jit()
    def fun_flat(
        self,
        u_flat: Float[jax.Array, " DoF"],
        q_flat: Float[jax.Array, " Q"] | None = None,
    ) -> Float[jax.Array, ""]:
        u_flat: Float[jax.Array, " D"] = self.fill_flat(u_flat)
        return self.problem.fun_flat(u_flat, q_flat)

    @override
    def prepare(self, q: PyTree | None = None) -> None:
        super().prepare(q)
        self.problem.prepare(q)
        self.fixed_values = self.get_param("fixed_values", q)

    @overload
    def ravel_q(self, q: PyTree) -> Float[jax.Array, " Q"]: ...
    @overload
    def ravel_q(self, q: None) -> None: ...  # pyright: ignore[reportOverlappingOverload]
    def ravel_q(self, q: PyTree | None) -> Float[jax.Array, " Q"] | None:
        return self.problem.ravel_q(q)

    def unravel_q(self, q_flat: Float[jax.Array, " Q"] | None) -> PyTree | None:
        return self.problem.unravel_q(q_flat)
