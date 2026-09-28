import * as THREE from 'three';
export function plateMaps(img, variant, { carbon = false } = {}) {
  const w = img.width, h = img.height;
  const src = document.createElement('canvas'); src.width = w; src.height = h;
  const sg = src.getContext('2d'); sg.drawImage(img, 0, 0);
  const m = sg.getImageData(0, 0, w, h).data;
  const mk = () => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
  const col = mk(), orm = mk(), bmp = mk();
  const cg = col.getContext('2d'), og = orm.getContext('2d'), bg = bmp.getContext('2d');
  const C = cg.createImageData(w, h), O = og.createImageData(w, h), B = bg.createImageData(w, h);
  // brushed-metal streaks (horizontal)
  const streak = new Float32Array(h);
  for (let y = 0; y < h; y++) streak[y] = (Math.random() - .5) * 0.10 + Math.sin(y * 0.9) * 0.015;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = (y * w + x) * 4, e = 1 - m[i] / 255;          // e = engraved amount
    let r, g, b, rough, metal;
    if (carbon) {
      const cell = ((Math.floor(x / 22) + Math.floor(y / 22)) & 1);
      const t = cell ? (x % 22) / 22 : (y % 22) / 22;
      const v = 8 + 16 * Math.pow(Math.sin(t * Math.PI), 2) + (cell ? 4 : 0);
      [r, g, b] = [v, v, v + 1]; rough = .38; metal = 0;
      if (e > .5) { [r, g, b] = [217, 175, 80]; rough = .25; metal = 1; }
    } else if (variant === 'gold') {
      const s = 1 + streak[y];
      [r, g, b] = [214 * s, 184 * s, 118 * s]; rough = .26; metal = 1;
      if (e > 0) { const k = e; r = r * (1 - k) + 92 * k; g = g * (1 - k) + 66 * k; b = b * (1 - k) + 24 * k; rough = .26 + .4 * k; }
    } else { // black lacquer with gold-filled engraving
      [r, g, b] = [14, 14, 15]; rough = .2; metal = 0;
      if (e > 0) { const k = e; r = 14 + (220 - 14) * k; g = 14 + (176 - 14) * k; b = 15 + (82 - 15) * k; rough = .2 + .1 * k; metal = k; }
    }
    C.data.set([r, g, b, 255], i);
    O.data.set([255, rough * 255, metal * 255, 255], i);
    const bv = 255 - e * 255; B.data.set([bv, bv, bv, 255], i);
  }
  cg.putImageData(C, 0, 0); og.putImageData(O, 0, 0); bg.putImageData(B, 0, 0);
  const map = new THREE.CanvasTexture(col); map.colorSpace = THREE.SRGBColorSpace;
  const ormT = new THREE.CanvasTexture(orm), bumpT = new THREE.CanvasTexture(bmp);
  for (const t of [map, ormT, bumpT]) t.anisotropy = 8;
  return new THREE.MeshPhysicalMaterial({ map, roughnessMap: ormT, metalnessMap: ormT, roughness: 1, metalness: 1,
    bumpMap: bumpT, bumpScale: 2.2, clearcoat: carbon ? .45 : variant === 'black' ? 1 : .3,
    clearcoatRoughness: carbon ? .25 : .08, envMapIntensity: carbon ? .35 : 1 });
}

