def polynomialAgreementSet {F : Type*} [Semiring F] [DecidableEq F] {ι : Type*} [Fintype ι]
    (domain : ι ↪ F) (received : ι → F) (P : F[X]) : Finset ι :=
  Finset.univ.filter fun i ↦ P.eval (domain i) = received i

def commonPolynomialAgreementSet {F : Type*} [Semiring F] [DecidableEq F] {ι : Type*} [Fintype ι]
    (domain : ι ↪ F) (f g : ι → F) (F₀ G₀ : F[X]) : Finset ι :=
  Finset.univ.filter fun i ↦ F₀.eval (domain i) = f i ∧ G₀.eval (domain i) = g i
