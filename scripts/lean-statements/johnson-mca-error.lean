theorem mcaError_affineLine_johnson_le
    {F : Type} [Field F] [Fintype F] [SampleableType F] {n D : ℕ} {eta : ℝ}
    (domain : Fin n ↪ F) (hD : 1 ≤ D) (hDn : D ≤ n - 2) (heta : 0 < eta)
    (ha : johnsonAgreement n D eta ≤ 1) :
    mcaError (AffineLineGenerator F) (code domain (D + 1)) (1 - johnsonAgreement n D eta) ≤
      min 1 (ENNReal.ofReal
        (johnsonExceptionCount n D ⌈johnsonAgreement n D eta * n⌉₊ eta /
          (Fintype.card F : ℝ)))
