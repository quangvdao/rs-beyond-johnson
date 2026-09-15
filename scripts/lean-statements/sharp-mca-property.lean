def HasSharpCapacityLineAgreement (δ : ℝ) (N : ℕ) (E : ℕ → ℝ) : Prop :=
  ∀ (n k A : ℕ),
    N ≤ n → 0 < k → k ≤ n → (k : ℝ) + δ * n ≤ A →
    ∀ (F : Type u) [Field F] [DecidableEq F],
      (k = 1 ∨ ringChar F = 0 ∨ k - 1 < ringChar F) →
      ∀ (domain : Fin n ↪ F) (f g : Fin n → F),
        ∃ exceptional : Finset F, (exceptional.card : ℝ) ≤ E n ∧
          ∀ z ∉ exceptional, ∀ P : F[X], P.degree < k →
            A ≤ (polynomialAgreementSet domain (fun i ↦ f i + z * g i) P).card →
            HasExactCorrelatedPair domain f g (RingHom.id F) k z P
