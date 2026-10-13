import React, {useMemo} from 'react';
import QRCode from 'qrcode';
import {C} from '../theme';

// Scannable QR (dark modules on ivory, 2-module quiet zone).
export const QR: React.FC<{value: string; size: number}> = ({value, size}) => {
  const {n, d} = useMemo(() => {
    const qr = QRCode.create(value, {errorCorrectionLevel: 'M'});
    const n = qr.modules.size;
    let d = '';
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (qr.modules.data[y * n + x]) d += `M${x} ${y}h1v1h-1z`;
    return {n, d};
  }, [value]);
  return (
    <svg width={size} height={size} viewBox={`-2 -2 ${n + 4} ${n + 4}`} shapeRendering="crispEdges">
      <rect x={-2} y={-2} width={n + 4} height={n + 4} fill={C.ivoire} />
      <path d={d} fill={C.noir} />
    </svg>
  );
};
