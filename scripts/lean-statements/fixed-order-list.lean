theorem exists_ratePartition_list_bound
    {R a : ℝ} {d : ℕ}
    (hR : 0 < R) (hRa : R < a) (haone : a < 1) (hd : 500 ≤ d)
    (hgate : 1 < ratePartitionGamma R a d) :
    ∃ p : RatePartitionFiniteParameters R a d,
      ∀ (F : Type u) [Field F] (n k A : ℕ),
      ratePartitionMathematicalLength R d p.multiplicity ≤ n → 0 < k →
      (k : ℝ) ≤ R * n →
      a * n ≤ A → A ≤ n →
      ∀ (domain : Fin n ↪ F) (received : Fin n → F),
      (ringChar F = 0 ∨
        max (max (k - 1) d) (ratePartitionJetBound R p.multiplicity) < ringChar F) →
      (closePolynomialSet domain received k A).Finite ∧
        ((closePolynomialSet domain received k A).ncard : ℝ) ≤
          (ratePartitionJetBound R p.multiplicity : ℝ) ^ 2 *
            (2 * ratePartitionJetBound R p.multiplicity / (a - R)) ^ d * n ^ d
