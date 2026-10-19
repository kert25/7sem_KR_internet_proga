/- Shared namespace for formalizations used by ProofLab. -/
namespace ProofLab

/-- A minimal theorem used to check the Lean integration during development. -/
theorem integration_smoke_test : True := by
  trivial

/--
Computes the maximum of a nonempty list represented by its first item and tail.
The result is obtained by a left fold of `Nat.max`.
-/
def maximumFrom (initial : Nat) (tail : List Nat) : Nat :=
  tail.foldl Nat.max initial

/-- The initial value never exceeds the computed maximum. -/
theorem initial_le_maximumFrom (initial : Nat) (tail : List Nat) :
    initial ≤ maximumFrom initial tail := by
  induction tail generalizing initial with
  | nil =>
      simp [maximumFrom]
  | cons head tail inductionHypothesis =>
      simp only [maximumFrom, List.foldl_cons]
      exact Nat.le_trans (Nat.le_max_left initial head) (inductionHypothesis (Nat.max initial head))

/--
Every item of the nonempty input list is less than or equal to `maximumFrom`.
This is the formalized postcondition of the maximum-search algorithm.
-/
theorem member_le_maximumFrom (initial value : Nat) (tail : List Nat)
    (membership : value ∈ initial :: tail) : value ≤ maximumFrom initial tail := by
  induction tail generalizing initial value with
  | nil =>
      simp only [maximumFrom, List.foldl_nil]
      simp only [List.mem_cons, List.not_mem_nil, or_false] at membership
      subst value
      exact Nat.le_refl initial
  | cons head rest inductionHypothesis =>
      simp only [maximumFrom, List.foldl_cons]
      simp only [List.mem_cons] at membership
      cases membership with
      | inl equalsInitial =>
          subst value
          exact Nat.le_trans (Nat.le_max_left initial head) (initial_le_maximumFrom (Nat.max initial head) rest)
      | inr memberOfTail =>
          cases memberOfTail with
          | inl equalsHead =>
              subst value
              exact Nat.le_trans (Nat.le_max_right initial head) (initial_le_maximumFrom (Nat.max initial head) rest)
          | inr memberOfRest =>
              apply inductionHypothesis (Nat.max initial head) value
              simp only [List.mem_cons]
              exact Or.inr memberOfRest

end ProofLab
