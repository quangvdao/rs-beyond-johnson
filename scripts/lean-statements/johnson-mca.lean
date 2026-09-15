theorem exists_exceptional_johnson_lineMCA_allChar
    /-

    D is the maximum candidate degree, A is the number of required agreements.
    -/
    (n D A : ℕ) (eta : ℝ)
    (hD : 1 ≤ D) (hDn : D ≤ n - 2) (heta : 0 < eta)
    /-

    a = sqrt(D/n) + eta; an integer A ≥ a*n represents the same agreement demand.
    -/
    (ha : johnsonAgreement n D eta ≤ 1)
    (hthreshold : johnsonAgreement n D eta * n ≤ A) (hAn : A ≤ n)
    /-

    An embedding ensures distinct evaluation points; no characteristic guard is needed.
    -/
    {F : Type*} [Field F] (domain : Fin n ↪ F) (f g : Fin n → F) :
    /-

    One exceptional set must work for all challenges and candidates quantified below.
    -/
    ∃ exceptional : Finset F,
      (exceptional.card : ℝ) ≤ johnsonE0 n D A eta ∧
      /-

      Every qualifying candidate outside the fixed exceptional set admits exact recovery.
      -/
      ∀ z ∉ exceptional, ∀ P : F[X], P.degree < D + 1 →
        A ≤ (polynomialAgreementSet domain (fun i ↦ f i + z * g i) P).card →
        HasExactCorrelatedPair domain f g (RingHom.id F) (D + 1) z P

theorem johnson_lineMCA_probability
    (n D : ℕ) (eta : ℝ)
    (hD : 1 ≤ D) (hDn : D ≤ n - 2) (heta : 0 < eta)
    (ha : johnsonAgreement n D eta ≤ 1)
    /-

    Finiteness is needed here for uniform sampling, not for the preceding theorems.
    -/
    {F : Type} [Field F] [Fintype F] (domain : Fin n ↪ F) :
    /-

    Uniform sampling divides the exceptional count by the field size; the cap is one.
    -/
    mcaError (AffineLineGenerator F) (code domain (D + 1))
        (1 - johnsonAgreement n D eta) ≤
      min 1 (ENNReal.ofReal
        (johnsonE0 n D (Nat.ceil (johnsonAgreement n D eta * n)) eta /
          (Fintype.card F : ℝ)))
