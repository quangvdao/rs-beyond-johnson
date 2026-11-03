theorem uniformExactInterleavedPowerAgreement_of_scalar (domain : ι ↪ F) {k L e : ℕ}
    (hscalar : ∀ w : Fin (ℓ + 1) → ι → F, UniformExactPowerAgreement domain w k L e)
    (hk : k ≤ L) (values : Fin (ℓ + 1) → ι → κ → F) :
    UniformExactInterleavedPowerAgreement domain values k L e
