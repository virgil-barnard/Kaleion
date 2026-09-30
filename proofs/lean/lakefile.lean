import Lake
open Lake DSL

package kaleionProofs where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @
  "6bd5e549d902323693ddf9128120376848331c85"

@[default_target]
lean_lib KaleionProofs
