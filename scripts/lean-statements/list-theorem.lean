theorem exists_rateCapacity_list
    (δ : ℝ) (hδ : 0 < δ) :
    HasCapacityLists δ (rateCapacityLengthThreshold δ)
      (fun n _ _ _ card => (card : ℝ) ≤ rateCapacityListBound δ n)
