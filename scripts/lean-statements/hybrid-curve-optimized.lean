theorem exists_exceptional_exact_powerAgreement_best_optimized
    {F E : Type u} [Field F] [Field E] [IsAlgClosed E]
    {p : LineProfile} (hp : p.CurveVerification)
    (split : ℕ)
    (hsplit : p.k ≤ split ∧ split ≤ p.agreement ∧ p.agreement ≤ p.n)
    (hk : 2 ≤ p.k) (hkn : p.k < p.n)
    (hell : 0 < p.batchingDegree)
    (hM : 1 ≤ p.firstDerivativeCap)
    (hMB : p.firstDerivativeCap ≤ p.totalJetCap)
    (domain : Fin p.n ↪ F)
    (values : Fin (p.batchingDegree + 1) → Fin p.n → F)
    (iota : F →+* E)
    (hchar : ringChar F = 0 ∨
      max p.D p.firstDerivativeCap < ringChar F) :
    ∃ exceptional : Finset F,
      (exceptional.card : ℝ) ≤ bestOptimizedCurveEnvelope p split ∧
      ∀ z ∉ exceptional, ∀ P : F[X], P.degree < p.k →
        p.agreement ≤
          (polynomialAgreementSet domain (powerBatchedWord values z) P).card →
        HasExactPowerAgreement domain values (RingHom.id F) p.k z P
