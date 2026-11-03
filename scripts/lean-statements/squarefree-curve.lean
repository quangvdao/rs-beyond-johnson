theorem exists_exceptional_retainedSquarefreeCurveAgreement_sharpAt
    {F E : Type*} [Field F] [Field E] [DecidableEq F] [DecidableEq E] [IsAlgClosed E]
    {n D ell L₀ L A B M H : ℕ}
    (domain : Fin n ↪ F) (values : Fin (ell + 1) → Fin n → F) (iota : F →+* E)
    (Q : DifferentialPolynomial E[X] 1) (hQ : Q ≠ 0)
    (hD : 1 ≤ D) (hDL₀ : D < L₀) (hL₀A : L₀ ≤ A)
    (hDL : D + 1 ≤ L) (hLA : L ≤ A) (hAn : A ≤ n)
    (hell : 0 < ell) (hM : 1 ≤ M) (hMB : M ≤ B)
    (hjet : jetTotalDegree Q ≤ B) (hderiv : Q.degreeOf (some 1) ≤ M)
    (hheight : CoeffNatDegreeLE Q H)
    (hchar : ringChar F = 0 ∨ max D M < ringChar F) :
    ∃ exceptional : Finset E,
      (exceptional.card : ℝ) ≤ retainedSquarefreeCurveSharpChargeAt n D ell L₀ L A B M H ∧
      ∀ z ∉ exceptional, ∀ P : E[X], P.degree < D + 1 →
        A ≤ (polynomialAgreementSet (domain.trans ⟨iota, iota.injective⟩)
          (powerBatchedWord (fun t i ↦ iota (values t i)) z) P).card →
        differentialSpecialization (challengeSpecialization Q z) P = 0 →
        HasExactPowerAgreement domain values iota (D + 1) z P

theorem exists_exceptional_retainedSquarefreeCurveAgreement_sharpOptimized
    {F E : Type*} [Field F] [Field E] [DecidableEq F] [DecidableEq E] [IsAlgClosed E]
    {n D ell L A B M H : ℕ}
    (domain : Fin n ↪ F) (values : Fin (ell + 1) → Fin n → F) (iota : F →+* E)
    (Q : DifferentialPolynomial E[X] 1) (hQ : Q ≠ 0)
    (hD : 1 ≤ D) (hDL : D + 1 ≤ L) (hLA : L ≤ A) (hAn : A ≤ n)
    (hell : 0 < ell) (hM : 1 ≤ M) (hMB : M ≤ B)
    (hjet : jetTotalDegree Q ≤ B) (hderiv : Q.degreeOf (some 1) ≤ M)
    (hheight : CoeffNatDegreeLE Q H)
    (hchar : ringChar F = 0 ∨ max D M < ringChar F) :
    ∃ exceptional : Finset E,
      (exceptional.card : ℝ) ≤ retainedSquarefreeCurveSharpOptimizedCharge n D ell L A B M H ∧
      ∀ z ∉ exceptional, ∀ P : E[X], P.degree < D + 1 →
        A ≤ (polynomialAgreementSet (domain.trans ⟨iota, iota.injective⟩)
          (powerBatchedWord (fun t i ↦ iota (values t i)) z) P).card →
        differentialSpecialization (challengeSpecialization Q z) P = 0 →
        HasExactPowerAgreement domain values iota (D + 1) z P
