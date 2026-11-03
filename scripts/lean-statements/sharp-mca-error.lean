theorem exists_capacity_mcaError {δ : ℝ} (hδ : 0 < δ) :
    ∃ N d : ℕ, ∃ C : ℝ, 4 ≤ N ∧ 0 < C ∧
      ∀ n k : ℕ, N ≤ n → 0 < k → k ≤ n →
      ∀ (F : Type) [Field F] [Fintype F] [SampleableType F],
        (ringChar F = 0 ∨ k - 1 < ringChar F) → ∀ domain : Fin n ↪ F,
          mcaError (AffineLineGenerator F) (code domain k) (capacityRadius δ n k) ≤
              ENNReal.ofReal (C * (n : ℝ) ^ (d + 1) / Fintype.card F) ∧
            ∀ s : ℕ, mcaError (AffineSpaceGenerator F s) (code domain k) (capacityRadius δ n k) ≤
              ENNReal.ofReal (C * (n : ℝ) ^ (d + 1) / ((Fintype.card F : ℝ) - 1))
