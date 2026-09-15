theorem fullSetLevelWitness_interleaved_of_exactAgreement
    {F : Type} [Field F] [Fintype F] [DecidableEq F]
    {n k agreement exceptionalCount width : ℕ}
    (domain : Fin n ↪ F)
    (hline : LineExactAgreementBound domain k agreement exceptionalCount)
    (hwidth : 0 < width) (hkAgreement : k ≤ agreement) :
    FullSetLevelWitness ((code domain k) ^⋈ (Fin width)) agreement exceptionalCount

theorem interleavedRS_tensorFoldBad_card_le_heightThree
    {F : Type} [Field F] [Fintype F] [DecidableEq F]
    {n k agreement exceptionalCount width : ℕ}
    (domain : Fin n ↪ F)
    (hline : LineExactAgreementBound domain k agreement exceptionalCount)
    (hwidth : 0 < width) (hkAgreement : k ≤ agreement)
    (u : (Fin 3 → Bool) → Fin n → Fin width → F) :
    (tensorFoldBad
      (fullSetLevelWitness_interleaved_of_exactAgreement domain hline hwidth hkAgreement) u).card ≤
        3 * exceptionalCount * Fintype.card F ^ 2
