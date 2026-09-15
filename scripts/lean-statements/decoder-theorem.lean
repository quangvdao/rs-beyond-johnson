theorem capacity_decoder_exact_output_and_primitive_work
    (delta : ℝ) (hdelta : 0 < delta) (hOne : delta < 1) :
    let d : ℕ := if (1 / 4 : ℝ) ≤ delta then 0
      else Nat.ceil (Real.exp (((27 : ℝ) / 10) / delta))
    let m : ℕ := Nat.ceil (100 * (d : ℝ) ^ 2 *
      ∑ i ∈ Finset.range (d - 1), (1 : ℝ) / (i + 1))
    let N : ℕ := if (1 / 4 : ℝ) ≤ delta then 1 else 8 * m
    ∃ C : ℕ, 0 < C ∧
      ∀ n k q A : ℕ, N ≤ n → 0 < k → k ≤ n → (hq : q.Prime) → n ≤ q →
        (k : ℝ) + delta * n ≤ A → A ≤ 2 * n →
        let : Fact q.Prime := ⟨hq⟩
        ∀ (alpha : Fin n ↪ ZMod q) (y : Fin n → ZMod q),
          ∃ (out : List (List (ZMod q))) (work : ℕ),
            ListDecoding.CoordinateCapacityMachine.run n k d m A
              (List.ofFn (fun i ↦ (alpha i, y i))) = (some out, work) ∧
            out.Nodup ∧ (out.map JetHornerMachine.coefficientPolynomial).Nodup ∧
            (∀ P : Polynomial (ZMod q),
              P ∈ out.map JetHornerMachine.coefficientPolynomial ↔
                P.degree < k ∧ A ≤ Code.agree (fun i ↦ P.eval (alpha i)) y) ∧
            (∀ cs : List (ZMod q), cs ∈ out ↔ cs.length = k ∧
              (JetHornerMachine.coefficientPolynomial cs).degree < k ∧
              A ≤ Code.agree (fun i ↦
                (JetHornerMachine.coefficientPolynomial cs).eval (alpha i)) y) ∧
            (n < A → out = []) ∧
            ((1 / 2 : ℝ) ≤ delta → out.length ≤ 1) ∧
            ((1 / 4 : ℝ) ≤ delta → out.length < n) ∧
            work ≤ C * q ^ (2 * d + 29) ∧
            (delta < (1 / 4 : ℝ) → out.length ≤ 4 * m * q ^ (2 * d) ∧
              (2 * (m * A + d - max k ⌊delta * (n : ℝ) / 2⌋₊) ≤ q →
                out.length ≤ 4 * m * q ^ d ∧ work ≤ C * q ^ (d + 29)))
