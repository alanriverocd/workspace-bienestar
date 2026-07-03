#!/bin/sh
case "$GIT_COMMIT" in
ce66839ee3fd4d0fae54159e6bea7e6a0c271579)
  printf '%s\n' "ci: aumentar espera de preview frontend a 12s antes de Playwright"
  ;;
a61ee1aec7a770f0c8ed2d61c710a6d4b7b548ed)
  printf '%s\n' "test(e2e): espera encabezado y aumenta timeouts para estabilidad en CI"
  ;;
*)
  cat
  ;;
esac
