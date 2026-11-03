theorem mathematicalUniform_capacity_list_bound
    (δ : ℝ) (hδ : 0 < δ) (hδsmall : δ < 6 / 25)
    (n k A : ℕ) (hn : uniformMathematicalCapacityLength δ ≤ n) (hk : 0 < k)
    (hgap : (k : ℝ) + δ * n ≤ A) (hAn : A ≤ n)
    {F : Type*} [Field F] (domain : Fin n ↪ F) (received : Fin n → F)
    (hchar : ringChar F = 0 ∨ k - 1 < ringChar F) :
    (closePolynomialSet domain received k A).Finite ∧
      ((closePolynomialSet domain received k A).ncard : ℝ) ≤
        mathematicalUniformListConstant δ * n ^ uniformDerivativeOrder δ
