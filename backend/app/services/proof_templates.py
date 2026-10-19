"""Lean templates approved for the algorithms available in the catalog."""

from collections.abc import Mapping


MAXIMUM_IN_LIST_TEMPLATE = """import ProofLab

namespace ProofLab

/-
The theorem states the key postcondition of a maximum-search algorithm:
every input element is less than or equal to the computed result.
-/
theorem maximum_in_list_correct (initial value : Nat) (tail : List Nat)
    (membership : value ∈ initial :: tail) : value ≤ maximumFrom initial tail := {{USER_PROOF}}

end ProofLab
"""


PROOF_TEMPLATES: Mapping[str, str] = {
    "maximum-in-list": MAXIMUM_IN_LIST_TEMPLATE,
}


def get_proof_template(slug: str) -> str | None:
    """Return the approved Lean template for an algorithm, if implemented."""

    return PROOF_TEMPLATES.get(slug)
