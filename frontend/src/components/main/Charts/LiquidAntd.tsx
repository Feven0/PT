import { Liquid } from '@ant-design/plots';
import React from 'react';

const LiquidAntd = ({ percent }) => {
  const config = {
    percent:  percent*0.01, 
    width: 100, 
    height: 100,
    style: {
      shape: (x, y, r) => {
        const path = [];
        const w = r * 2;

        for (let i = 0; i < 5; i++) {
          path.push([
            i === 0 ? 'M' : 'L',
            (Math.cos(((18 + i * 72) * Math.PI) / 180) * w) / 2 + x,
            (-Math.sin(((18 + i * 72) * Math.PI) / 180) * w) / 2 + y,
          ]);
          path.push([
            'L',
            (Math.cos(((54 + i * 72) * Math.PI) / 180) * w) / 4 + x,
            (-Math.sin(((54 + i * 72) * Math.PI) / 180) * w) / 4 + y,
          ]);
        }
        path.push(['Z']);
        return path;
      },
      outlineBorder: 0,
      outlineDistance: 0,
      waveLength: 128,
    },
  };

  return <Liquid {...config} />;
};

export default LiquidAntd;