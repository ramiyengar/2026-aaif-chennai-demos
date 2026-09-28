export const hashPassword = (password, salt) => {
  const scrypt = require('crypto').scryptSync;
  return scrypt(password, salt, 64).toString('base64');
}