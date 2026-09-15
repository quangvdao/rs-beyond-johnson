theorem exists_sharpCapacity_lineAgreement (δ : ℝ) (hδ : 0 < δ) :
    ∃ N d : ℕ, ∃ C : ℝ, 4 ≤ N ∧ 0 < C ∧
      HasSharpCapacityLineAgreement δ N (fun n ↦ C * (n : ℝ) ^ (d + 1))
