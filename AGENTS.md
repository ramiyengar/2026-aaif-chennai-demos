# AI Agent Instructions

- **Package Manager:** We use `pnpm` exclusively. Never use `npm` or `yarn`.
- **Crypto:** Do not use external hashing libraries (no bcrypt). Use the native Node `crypto` module (`scryptSync`).
- **Style:** Use functional programming patterns. No classes.
- **Testing:** Write `vitest` tests inline within the same file.
- **Architecture:** All new utilities MUST go in `src/core/utils/`.
