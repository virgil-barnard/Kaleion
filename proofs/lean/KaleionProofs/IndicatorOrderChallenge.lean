module

import Mathlib

set_option autoImplicit false

namespace KaleionProofs

/- Kaleion statement: none
   Kaleion goal: d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6
   This definition states a proposition; it is not a proof. -/
public abbrev kaleionGoal_d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6 : Prop :=
  ∀ (p0 p1 : ℤ), (((if (p0 ≤ p1) then (1 : ℤ) else (0 : ℤ)) + (if (p1 ≤ p0) then (1 : ℤ) else (0 : ℤ))) = ((1 : ℤ) + (if (p0 = p1) then (1 : ℤ) else (0 : ℤ))))

end KaleionProofs
