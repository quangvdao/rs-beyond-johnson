def HasCapacityLists (δ : ℝ) (N : ℕ)
    (bounds : ℕ → ℕ → ℕ → ℕ → ℕ → Prop) : Prop :=
  ∀ n k q A : ℕ,
    N ≤ n →
    0 < k → k ≤ n →
    q.Prime → n ≤ q →
    (k : ℝ) + δ * n ≤ A → A ≤ 2 * n →
    ∀ (α : Fin n ↪ ZMod q) (y : Fin n → ZMod q),
      ∃ list : Finset (Polynomial (ZMod q)),
        (∀ P, P ∈ list ↔
          P.degree < k ∧ A ≤ Code.agree (fun i => P.eval (α i)) y) ∧
        (n < A → list = ∅) ∧
        bounds n k q A list.card
