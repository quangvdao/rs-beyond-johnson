theorem exists_ratePartition_line_exactCorrelatedPair_parameters
    {R a : ℝ} {d : ℕ}
    (hR : 0 < R) (hRa : R < a) (haone : a < 1) (hd : 500 ≤ d)
    (hgate : 1 < RatePartition.rateGamma R a d) :
    ∃ p : RatePartition.PartitionFiniteParameters R a d,
      ∀ (F : Type u) [Field F] (n k A : ℕ),
      RatePartition.rateBlockThreshold R d p.multiplicity ≤ n → 0 < k →
      (k : ℝ) ≤ R * n → a * n ≤ A → A ≤ n →
      ∀ (domain : Fin n ↪ F) (f g : Fin n → F),
      (ringChar F = 0 ∨
        max (max (k - 1) d) (RatePartition.rateJetCap R p.multiplicity) < ringChar F) →
      ∃ exceptional : Finset F,
        (exceptional.card : ℝ) ≤ polynomialCurveProductAgreementConstant (a - R)
          (RatePartition.rateJetCap R p.multiplicity)
          (RatePartition.marginHeight (RatePartition.rateJetCap R p.multiplicity)
            (RatePartition.partitionFiniteRatio R a d p.multiplicity)) d * (n : ℝ) ^ (d + 1) ∧
        ∀ z ∉ exceptional,
          ∀ P : F[X], P.degree < k →
          A ≤ (polynomialAgreementSet domain (fun i ↦ f i + z * g i) P).card →
          HasExactCorrelatedPair domain f g (RingHom.id F) k z P
