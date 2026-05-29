export const extractInitials = (name: string) => {
  const names: string[] = name.split(" ")
  if (names.length === 1) {
    return names[0][0]?.toUpperCase()
  } else {
    return [names[0][0], names[1][0]].join("")?.toUpperCase()
  }
}

export const isURL = (str: string) => {
  const pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
    '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
    '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
    '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
    '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
    '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return !!pattern.test(str);
}