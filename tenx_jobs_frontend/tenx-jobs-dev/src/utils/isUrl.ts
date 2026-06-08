export const isURL = (str: string) => {
  const pattern = new RegExp('^(https?:\\/\\/)?'+ 
    '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+
    '((\\d{1,3}\\.){3}\\d{1,3}))'+ 
    '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ 
    '(\\?[;&a-z\\d%_.~+=-]*)?'+ 
    '(\\#[-a-z\\d_]*)?$','i'); 
  return !!pattern.test(str);
}

export const ensureURLProtocol = (url:string) => {
  if (!/^(https?:\/\/)/i.test(url)) {
    return `http://${url}`;
  }
  return url;
}