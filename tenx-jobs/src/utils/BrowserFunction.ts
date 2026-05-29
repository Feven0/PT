import { AESDecrypt, AESEncrypt } from "./CryptoHelper";

export async function copyTextToClipboard(text: string) {
  if ("clipboard" in navigator) {
    return await navigator.clipboard.writeText(text);
  } else {
    return document.execCommand("copy", true, text);
  }
}

export function setWithExpiry(key: string, value: string, ttl: number) {
  const now = new Date();
  const item = {
    value: value,
    expiry: now.getTime() + ttl,
  };
  localStorage.setItem(key, AESEncrypt(JSON.stringify(item)));
}

export function getWithExpiry(key: string) {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) {
    return null;
  }
  try {
    const item = JSON.parse(AESDecrypt(itemStr));
    const now = new Date();
    if (now.getTime() > item?.expiry) {
      // and return null
      localStorage.removeItem(key);
      return null;
    }
    return item?.value;
  } catch (error) {
    return null;
  }
}
