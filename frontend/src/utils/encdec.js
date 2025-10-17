// encdec.js
// Ecryption and decryption functions
// Derived from a conversation with ChatGPT: https://chatgpt.com/share/68856dd9-6548-800f-8c70-038ffbb58d86


// Utility: Convert string to ArrayBuffer
function strToBuf(str) {
  return new TextEncoder().encode(str);
}

// Utility: Convert ArrayBuffer to string
function bufToStr(buf) {
  return new TextDecoder().decode(buf);
}

// Utility: Generate random bytes
function getRandomBytes(length) {
  return window.crypto.getRandomValues(new Uint8Array(length));
}

// Derive key from password and salt using PBKDF2
async function deriveKey(password, salt) {
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    strToBuf(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt,
      iterations: 100_000,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}


function bufToB64(buf) {
  return btoa(String.fromCharCode(...buf));
}

function b64ToBuf(b64) {
  return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

export default async function encryptJson(jsonObj, password) {
  const salt = getRandomBytes(16);
  const iv = getRandomBytes(12);
  const key = await deriveKey(password, salt);
  const plaintext = strToBuf(JSON.stringify(jsonObj));

  const ciphertext = new Uint8Array(await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    plaintext
  ));

  // Combine all pieces into a single string
  const bundle = [
    bufToB64(salt),
    bufToB64(iv),
    bufToB64(ciphertext)
  ].join(':');

  return bundle;
}

 export async function decryptJson(bundle, password) {
  const [saltB64, ivB64, ciphertextB64] = bundle.split(':');
  const salt = b64ToBuf(saltB64);
  const iv = b64ToBuf(ivB64);
  const ciphertext = b64ToBuf(ciphertextB64);

  const key = await deriveKey(password, salt);
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    ciphertext
  );

  return JSON.parse(bufToStr(decrypted));
}

// Example usage
async function main() {

    const password = "secret";
    const json = { user: "alice", roles: ["admin"] };

    const encrypted = await encryptJson(json, password);
    console.log("Encrypted string to store:", encrypted);

    // Later...
    const decrypted = await decryptJson(encrypted, password);
    console.log("Decrypted JSON:", decrypted);

}

// main();