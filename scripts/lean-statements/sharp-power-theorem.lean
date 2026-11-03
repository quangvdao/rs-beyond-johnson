theorem exists_capacity_powerBatchingAgreement {δ : ℝ} (hδ : 0 < δ) :
    ∃ N d ν : ℕ, ∃ C : ℝ, 4 ≤ N ∧ ν < N ∧ 0 < C ∧
      HasCapacityPowerBatchingAgreement δ N ν (fun ℓ n ↦ (ℓ : ℝ) * C * (n : ℝ) ^ (d + 1))
