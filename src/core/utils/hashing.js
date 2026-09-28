// Function to securely hash user passwords
const { scryptSync } = require('crypto');
const SCRYPT_N = 16384;
const SCRYPT_P = 8;
const SCRYPT_r = 8;
const DEFAULT_SALT_LENGTH = 32;

function hashPassword(password, salt) {
    if (!salt) {
        salt = crypto.randomBytes(DEFAULT_SALT_LENGTH);
    }
    return scryptSync(password, salt, 64)
        .toString('base64');
}

// Example usage:
// const hashedPassword = hashPassword('user_password', 'optional_custom_salt')