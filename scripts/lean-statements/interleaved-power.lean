theorem uniformExactInterleavedPowerAgreement_of_scalar_arbitrary
    [DecidableEq F]
    {n k agreement exceptionalCount width ℓ : ℕ}
    (domain : Fin n ↪ F)
    (hscalar : ∀ values : Fin (ℓ + 1) → Fin n → F,
      UniformExactPowerAgreement domain values k agreement exceptionalCount)
    (hwidth : 0 < width) (hkAgreement : k ≤ agreement)
    (values : Fin (ℓ + 1) → Fin n → Fin width → F) :
    UniformExactInterleavedPowerAgreement domain values k agreement exceptionalCount
