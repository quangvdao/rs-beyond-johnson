theorem tensorFoldBad_card_le [Fintype F] [DecidableEq A]
    {C : ModuleCode ι F A} {agreement exceptionalCount h : ℕ}
    (hlevel : FullSetLevelWitness C agreement exceptionalCount)
    (u : (Fin h → Bool) → ι → A) :
    (tensorFoldBad hlevel u).card ≤
      h * exceptionalCount * Fintype.card F ^ (h - 1)
