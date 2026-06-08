import * as CryptoJS from "crypto-js";

function getCurrentDateFormatted(): string {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, "0");
  const day = String(currentDate.getDate()).padStart(2, "0");
  return `${day}/${month}/${year}`;
}

export function AESEncrypt(text: string) {
  const dynamicValue = getCurrentDateFormatted(); 
  const privateKey = `${dynamicValue} secret key 123`;
  const ciphertext = CryptoJS.AES.encrypt(text, privateKey).toString();
  return ciphertext;
}

export function AESDecrypt(text: string) {
  const dynamicValue = getCurrentDateFormatted(); 
  const privateKey = `${dynamicValue} secret key 123`;
  const bytes = CryptoJS.AES.decrypt(text, privateKey);
  const decryptedData = bytes.toString(CryptoJS.enc.Utf8);
  return decryptedData;
}


