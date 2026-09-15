theorem uniform_capacity_list_bound_300
    /-

    Fix the capacity gap and its small-gap regime.
    -/
    (δ : ℝ)
    (hδ : 0 < δ)
    (hδsmall : δ < 6 / 25)
    /-

    The sufficient length depends only on delta, not on the field or received word.
    -/
    (n k A : ℕ)
    (hn : uniformCapacityLengthThreshold300 δ ≤ n)
    (hk : 0 < k)
    /-

    Agreement is measured in positions, and message degree is strictly below k.
    -/
    (hgap : (k : ℝ) + δ * n ≤ A)
    (hAn : A ≤ n)
    /-

    An embedding records that all n evaluation points are distinct.
    -/
    {F : Type*} [Field F]
    (domain : Fin n ↪ F)
    (received : Fin n → F)
    (hchar : ringChar F = 0 ∨ k - 1 < ringChar F) :
    let d := uniformRatePartitionOrder δ
    let C : ℝ := uniformCapacityListConstant300 δ
    /-

    Both conclusions concern the complete list, not a selected sublist.
    -/
    (closePolynomialSet domain received k A).Finite ∧
      ((closePolynomialSet domain received k A).ncard : ℝ) ≤ C * n ^ d
