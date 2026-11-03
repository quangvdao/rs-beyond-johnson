theorem fullSetLevelWitness_interleaved_of_exactAgreement (domain : ι ↪ F) {k L e : ℕ}
    (hline : ∀ w : Fin 2 → ι → F, UniformExactPowerAgreement domain w k L e) (hk : k ≤ L)
    (κ : Type) [Fintype κ] : FullSetLevelWitness ((code domain k)^⋈κ) L e

theorem interleavedRS_tensorFoldBad_card_le_heightThree [Fintype F] (domain : ι ↪ F) {k L e : ℕ}
    (hline : ∀ w : Fin 2 → ι → F, UniformExactPowerAgreement domain w k L e) (hk : k ≤ L)
    {κ : Type} [Fintype κ] (u : (Fin 3 → Bool) → ι → κ → F) :
    (tensorFoldBad (fullSetLevelWitness_interleaved_of_exactAgreement domain hline hk κ) u).card ≤
      3 * e * Fintype.card F ^ 2
