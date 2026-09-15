theorem exists_sharpCapacity_powerBatchingAgreement (δ : ℝ) (hδ : 0 < δ) :
    ∃ N d : ℕ, ∃ C : ℝ, 4 ≤ N ∧ 0 < C ∧
      HasSharpCapacityPowerBatchingAgreement δ N
        (fun ell n ↦ (ell : ℝ) * C * (n : ℝ) ^ (d + 1))
