def HasCapacityLineAgreement (δ : ℝ) (N : ℕ) (E : ℕ → ℝ) : Prop :=
  ∀ n k A : ℕ, N ≤ n → 0 < k → (k : ℝ) + δ * n ≤ A →
    ∀ (F : Type u) [Field F] [DecidableEq F], (ringChar F = 0 ∨ k - 1 < ringChar F) →
      ∀ domain : Fin n ↪ F, LineExactAgreementBound domain k A (E n)
