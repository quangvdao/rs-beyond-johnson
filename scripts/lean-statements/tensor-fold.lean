theorem tensorFoldBad_card_le [Fintype F] (hlevel : FullSetLevelWitness C a e) {h : ℕ}
    (u : (Fin h → Bool) → ι → A) :
    (tensorFoldBad hlevel u).card ≤ h * e * Fintype.card F ^ (h - 1)
