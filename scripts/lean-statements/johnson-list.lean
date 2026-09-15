theorem closePolynomialSet_finite_and_ncard_le_johnsonPairwise
    {F : Type*} [Field F] {n D A : ℕ}
    (domain : Fin n ↪ F) (received : Fin n → F)
    (hDA : D + 1 ≤ A) (hpositive : n * D < A * A) :
    (closePolynomialSet domain received (D + 1) A).Finite ∧
      (closePolynomialSet domain received (D + 1) A).ncard ≤
        johnsonPairwiseListFloor n D A
