import pluralize from "pluralize";

export const getSingularPluralString = (
  length: number,
  name: string | undefined
): string => {
  const validName = name ? name : ""; 
  return length > 1 ? `${length} ${pluralize(validName)}` : `${length} ${validName}`;
};
