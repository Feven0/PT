export const getRandomColor = (email: string) => {
  const hash = email?.split("").reduce((acc, char) => {
    const charCode = char.charCodeAt(0);
    return (acc << 5) - acc + charCode;
  }, 0);

  const backgroundColor = `hsl(${hash % 360}, 70%, 80%)`;

  const getContrastYIQ = (hexcolor: string) => {
    const r = parseInt(hexcolor.substring(1, 3), 16);
    const g = parseInt(hexcolor.substring(3, 5), 16);
    const b = parseInt(hexcolor.substring(5, 7), 16);
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;
    return yiq;
  };

  const textColor =
    getContrastYIQ(backgroundColor) >= 128 ? "#FFFFFF" : "#000000";

  return {
    backgroundColor: backgroundColor,
    textColor: textColor,
  };
};
