def agree (u v : n → R) : ℕ := ({i | u i = v i} : Finset _).card
