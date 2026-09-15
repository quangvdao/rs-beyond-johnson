def polynomialAgreementSet {F : Type*} [Field F] [DecidableEq F] {n : ℕ}
    (domain : Fin n ↪ F) (received : Fin n → F) (P : F[X]) : Finset (Fin n) :=
  Finset.univ.filter fun i ↦ P.eval (domain i) = received i

def commonPolynomialAgreementSet {F : Type*} [Field F] [DecidableEq F] {n : ℕ}
    (domain : Fin n ↪ F) (f g : Fin n → F) (F₀ G₀ : F[X]) : Finset (Fin n) :=
  Finset.univ.filter fun i ↦ F₀.eval (domain i) = f i ∧ G₀.eval (domain i) = g i
