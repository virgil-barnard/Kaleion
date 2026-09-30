module

import KaleionProofs.IndicatorOrderChallenge

set_option autoImplicit false

namespace KaleionProofs

theorem indicatorOrderProof :
    kaleionGoal_d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6 := by
  intro x y
  by_cases hxy : x ≤ y <;> by_cases hyx : y ≤ x <;>
    simp [hxy, hyx] <;> omega

#print axioms indicatorOrderProof

end KaleionProofs
