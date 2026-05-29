type Style = {
  padding: string;
  background: string;
  color: string;
  borderRadius: string;
};

export const getSfiaLevelStyle = (sf: string): Style => {
  let background: string;
  let color: string;
  const sfia_level = Number(sf);

  if (sfia_level === 7) {
    background = '#F6FFED';
    color = '#52C41A';
  } else if (sfia_level >= 5) {
    background = '#E6F4FF';
    color = '#1677FF';
  } else if (sfia_level >= 3) {
    background = '#FFF7E6';
    color = '#FA8C16';
  } else if (sfia_level >= 1) {
    background = '#FFFBE6';
    color = '#874D00';
  } else {
    background = '#F5F5F5';
    color = 'rgba(0, 0, 0, 0.65)';
  }

  return {
    padding: "0.5rem 1rem",
    background,
    color,
    borderRadius: '4px',
  };
};
