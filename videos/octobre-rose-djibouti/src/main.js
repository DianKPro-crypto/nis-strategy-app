// Octobre Rose Djibouti 2026 — 9:16 3D motion piece.
// Everything is a pure function of time t (seconds): window.renderAt(t) draws one frame.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { TTFLoader } from 'three/addons/loaders/TTFLoader.js';
import { Font } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

const W = 1080, H = 1920;
const params = new URLSearchParams(location.search);
const SHOW_PARTNERS = params.get('partners') !== '0';

// ---------------------------------------------------------------- helpers
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const smooth = (x) => x * x * (3 - 2 * x);
const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = (x) => 1 - Math.pow(1 - x, 3);
const easeIn = (x) => x * x * x;
const win = (t, a, b, di = 0.5, dout = 0.45) => Math.min(easeOut(prog(t, a, a + di)), 1 - easeIn(prog(t, b - dout, b)));
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

// ---------------------------------------------------------------- renderer
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0b0c);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.75;

const camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 200);
scene.add(camera);

const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1);
composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.5, 0.45, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- lights
const key = new THREE.DirectionalLight(0xffe2b0, 1.6); key.position.set(3, 5, 6); scene.add(key);
const fill = new THREE.DirectionalLight(0xff7aa8, 0.9); fill.position.set(-5, -2, 3); scene.add(fill);
const rimL = new THREE.PointLight(0xff2a7a, 30, 30, 1.6); rimL.position.set(0, 2, -4); scene.add(rimL);
const sweep = new THREE.PointLight(0xffffff, 0, 12, 1.5); scene.add(sweep);

// ---------------------------------------------------------------- backdrop (camera-attached radial glows)
const backdrop = new THREE.Mesh(
  new THREE.PlaneGeometry(26, 44),
  new THREE.ShaderMaterial({
    depthWrite: false,
    uniforms: { uPink: { value: 0.35 }, uGold: { value: 0.18 }, uPinkPos: { value: new THREE.Vector2(0.5, 0.78) }, uGoldPos: { value: new THREE.Vector2(0.5, 0.12) } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: `varying vec2 vUv; uniform float uPink,uGold; uniform vec2 uPinkPos,uGoldPos;
      void main(){ vec2 a=vec2(1.0,1.69);
        float dp=length((vUv-uPinkPos)*a); float dg=length((vUv-uGoldPos)*a);
        vec3 base=vec3(0.0034,0.0034,0.0037);
        vec3 c=base+vec3(1.0,0.03,0.18)*uPink*exp(-dp*dp*5.0)*0.12+vec3(0.66,0.38,0.07)*uGold*exp(-dg*dg*6.0)*0.12;
        gl_FragColor=vec4(c,1.0);}`,
  })
);
backdrop.position.set(0, 0, -60);
camera.add(backdrop);

// ---------------------------------------------------------------- dust / bokeh
function softPointsMaterial(extra = {}) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uAlpha: { value: 1 }, uSize: { value: 1 }, ...extra.uniforms },
    vertexShader: extra.vertexShader, fragmentShader: extra.fragmentShader,
  });
}
const dust = (() => {
  const n = 1400, r = rng(7), pos = new Float32Array(n * 3), col = new Float32Array(n * 3), sp = new Float32Array(n);
  const pink = new THREE.Color(0xff2a7a), gold = new THREE.Color(0xe3b34c);
  for (let i = 0; i < n; i++) {
    pos.set([(r() - 0.5) * 9, (r() - 0.5) * 13, -8 + r() * 10], i * 3);
    const c = r() < 0.55 ? gold : pink; col.set([c.r, c.g, c.b], i * 3); sp[i] = 0.05 + r() * 0.18;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSpeed', new THREE.BufferAttribute(sp, 1));
  const m = softPointsMaterial({
    vertexShader: `uniform float uTime,uSize; attribute float aSpeed; attribute vec3 color; varying vec3 vC; varying float vF;
      void main(){ vec3 p=position; p.y=mod(p.y+uTime*aSpeed+6.5,13.0)-6.5; p.x+=sin(uTime*0.4+position.z*2.0+position.y)*0.15;
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
        float d=-mv.z; gl_PointSize=uSize*(6.0+aSpeed*40.0)*(10.0/d); vF=smoothstep(22.0,6.0,d); vC=color;}`,
    fragmentShader: `uniform float uAlpha; varying vec3 vC; varying float vF;
      void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vC*a*a*0.9*uAlpha*vF,1.0);}`,
  });
  const pts = new THREE.Points(g, m); pts.frustumCulled = false; scene.add(pts); return pts;
})();

// ---------------------------------------------------------------- materials with fresnel neon rim
function withRim(mat, color, strength) {
  mat.userData.rim = { value: strength };
  mat.userData.rimColor = { value: new THREE.Color(color) };
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uRim = mat.userData.rim; sh.uniforms.uRimColor = mat.userData.rimColor;
    sh.fragmentShader = 'uniform float uRim; uniform vec3 uRimColor;\n' + sh.fragmentShader.replace('#include <emissivemap_fragment>',
      `#include <emissivemap_fragment>
       float fr = pow(1.0 - abs(dot(normal, normalize(vViewPosition))), 2.6);
       totalEmissiveRadiance += uRimColor * fr * uRim;`);
  };
  return mat;
}
const pinkMat = () => withRim(new THREE.MeshPhysicalMaterial({ color: 0xe6005c, roughness: 0.3, metalness: 0.05, sheen: 0.5, sheenColor: new THREE.Color(0xff3d84), sheenRoughness: 0.45, clearcoat: 0.35, clearcoatRoughness: 0.3, envMapIntensity: 0.35, emissive: 0x4a0018, transparent: true }), 0xff2a7a, 1.15);
const goldMat = () => withRim(new THREE.MeshPhysicalMaterial({ color: 0xd4a44c, roughness: 0.24, metalness: 1, clearcoat: 0.6, clearcoatRoughness: 0.2, transparent: true }), 0xffcf70, 1.6);

// ---------------------------------------------------------------- ribbon builder
class Ribbon {
  constructor({ N = 260, M = 14, width = 0.36, thick = 0.05, material }) {
    this.N = N; this.M = M; this.width = width; this.thick = thick;
    const g = new THREE.BufferGeometry();
    this.pos = new Float32Array(N * M * 3);
    g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    const idx = [];
    for (let i = 0; i < N - 1; i++) for (let j = 0; j < M; j++) {
      const a = i * M + j, b = i * M + ((j + 1) % M), c = (i + 1) * M + j, d = (i + 1) * M + ((j + 1) % M);
      idx.push(a, c, b, b, c, d);
    }
    g.setIndex(idx);
    this.geo = g;
    this.mesh = new THREE.Mesh(g, material);
    this.mesh.frustumCulled = false;
    this.cs = [];
    for (let j = 0; j < M; j++) { const a = (j / M) * Math.PI * 2; this.cs.push([Math.cos(a) * 0.5, Math.sin(a) * 0.5]); }
    this.P = Array.from({ length: N }, () => V());
    scene.add(this.mesh);
  }
  // fn(u) -> Vector3 (written into out); u0..u1 drawn range; widthScale; twist(u)
  update(fn, { u0 = 0, u1 = 1, w = 1, taper = 0.06, closed = false, twist = () => 0 } = {}) {
    const { N, M, P } = this;
    for (let i = 0; i < N; i++) fn(lerp(u0, u1, i / (N - 1)), P[i]);
    const T = V(), Wd = V(), B = V(), Z = V(0, 0, 1), tmp = V();
    for (let i = 0; i < N; i++) {
      const a = P[Math.max(0, i - 1)], b = P[Math.min(N - 1, i + 1)];
      if (closed && (i === 0 || i === N - 1)) { T.subVectors(P[1], P[N - 2]); } else T.subVectors(b, a);
      T.normalize();
      Wd.crossVectors(Z, T); if (Wd.lengthSq() < 1e-6) Wd.set(1, 0, 0); Wd.normalize();
      B.crossVectors(T, Wd).normalize();
      const s = i / (N - 1), u = lerp(u0, u1, s);
      const ang = twist(u);
      tmp.copy(Wd).multiplyScalar(Math.cos(ang)).addScaledVector(B, Math.sin(ang)); B.crossVectors(T, tmp).normalize(); Wd.copy(tmp);
      let ws = w;
      if (!closed && taper > 0) ws *= smooth(clamp(s / taper)) * smooth(clamp((1 - s) / taper));
      const hw = this.width * ws, ht = this.thick * Math.max(ws, 0.15);
      for (let j = 0; j < M; j++) {
        const [cx, cy] = this.cs[j], k = (i * M + j) * 3;
        this.pos[k] = P[i].x + Wd.x * cx * hw * 2 + B.x * cy * ht * 2;
        this.pos[k + 1] = P[i].y + Wd.y * cx * hw * 2 + B.y * cy * ht * 2;
        this.pos[k + 2] = P[i].z + Wd.z * cx * hw * 2 + B.z * cy * ht * 2;
      }
    }
    this.geo.attributes.position.needsUpdate = true;
    this.geo.computeVertexNormals();
  }
  set visible(v) { this.mesh.visible = v; }
  set opacity(o) { this.mesh.material.opacity = o; this.mesh.visible = o > 0.004; }
}

// ---------------------------------------------------------------- shapes
const awCurve = new THREE.CatmullRomCurve3([
  V(-0.98, -1.88, 0.10), V(-0.55, -1.05, 0.11), V(0.0, -0.22, 0.13), V(0.46, 0.52, 0.06), V(0.6, 1.12, 0.0),
  V(0.36, 1.6, -0.05), V(0.0, 1.74, -0.08), V(-0.36, 1.6, -0.05), V(-0.6, 1.12, 0.0), V(-0.46, 0.52, -0.06),
  V(0.0, -0.22, -0.13), V(0.55, -1.05, -0.11), V(0.98, -1.88, -0.10),
], false, 'centripetal');
const awareness = (u, o, s = 1, cx = 0, cy = 0) => { awCurve.getPointAt(clamp(u), o); return o.multiplyScalar(s).add(V(cx, cy + 0.07 * s, 0)); };
const serpent = (u, o, t, x0 = 0, amp = 0.5, ph = 0, len = 10, freq = 7.0) => {
  const a = u * freq + ph + t * 0.9;
  return o.set(x0 + amp * Math.sin(a), lerp(-len / 2, len / 2, u), amp * 0.65 * Math.cos(a));
};
const centre = (u, o, t) => serpent(u, o, t, 0, 0.22, 1.3, 10, 4.5);
const helixAround = (u, o, t, r = 0.42) => {
  centre(u, o, t); const a = u * 15 + t * 1.6;
  return o.add(V(r * Math.cos(a), 0, r * Math.sin(a)));
};
const ring = (u, o, t, R = 1.45, cy = 0.15, rot = 0) => { const a = u * Math.PI * 2 + Math.PI / 2 + rot; return o.set(R * Math.cos(a), cy + R * Math.sin(a), 0); };
const torusHelix = (u, o, t, R = 1.45, cy = 0.15, r = 0.24, rot = 0, turns = 8) => {
  const a = u * Math.PI * 2 + Math.PI / 2 + rot, b = u * Math.PI * 2 * turns + t * 1.2;
  const rr = R + r * Math.cos(b);
  return o.set(rr * Math.cos(a), cy + rr * Math.sin(a), r * Math.sin(b));
};
const awHelix = (u, o, t, s, cx, cy, r = 0.085, turns = 9) => {
  const p = awareness(u, V(), s, cx, cy), q = awareness(clamp(u + 0.002), V(), s, cx, cy);
  const T = q.sub(p).normalize(), N = V(0, 0, 1).cross(T).normalize();
  const b = u * Math.PI * 2 * turns + t * 1.4;
  return o.copy(p).addScaledVector(N, r * s * Math.cos(b)).add(V(0, 0, r * s * Math.sin(b)));
};
// blend two shapes with a travelling wave along u
const morph = (fa, fb, m, u, o) => {
  const w = smooth(clamp(m * 1.6 - u * 0.6));
  const a = fa(u, V()), b = fb(u, V());
  return o.copy(a).lerp(b, w);
};

// ---------------------------------------------------------------- ribbons
const pink = new Ribbon({ material: pinkMat(), width: 0.36, thick: 0.05 });
const gold = new Ribbon({ material: goldMat(), width: 0.3, thick: 0.045 });
const filCols = [0xff2a7a, 0xff6fa0, 0xe6005c];
const fils = filCols.map((c) => { const m = pinkMat(); m.color.set(c); m.userData.rim.value = 3.0; return new Ribbon({ material: m, width: 0.13, thick: 0.03, N: 200, M: 10 }); });

// ---------------------------------------------------------------- 3D title
let title = null;
async function makeTitle() {
  const json = await new Promise((res, rej) => new TTFLoader().load('/node_modules/@expo-google-fonts/playfair-display/PlayfairDisplay_700Bold.ttf', res, undefined, rej));
  const font = new Font(json);
  const geo = new TextGeometry('OCTOBRE ROSE', { font, size: 0.42, depth: 0.09, curveSegments: 10, bevelEnabled: true, bevelThickness: 0.018, bevelSize: 0.011, bevelSegments: 3 });
  geo.computeBoundingBox(); const bb = geo.boundingBox;
  geo.translate(-(bb.max.x + bb.min.x) / 2, -(bb.max.y + bb.min.y) / 2, 0);
  const width = bb.max.x - bb.min.x, s = Math.min(1, 3.75 / width);
  const mat = withRim(new THREE.MeshPhysicalMaterial({ color: 0xe6a832, metalness: 0.75, roughness: 0.5, clearcoat: 0.0, envMapIntensity: 0.55, emissive: 0x0a0500, transparent: true }), 0xffb84a, 0.12);
  title = new THREE.Mesh(geo, mat); title.scale.setScalar(s); scene.add(title);
}

// ---------------------------------------------------------------- mammograph hologram (particles)
const mammo = (() => {
  const r = rng(42), tgt = [], kind = [];
  const box = (cx, cy, cz, sx, sy, sz, n, k = 0, edge = 0.35) => {
    const faces = [[sx, sy, 2], [sx, sy, -2], [sx, sz, 1], [sx, sz, -1], [sy, sz, 0], [sy, sz, -0]];
    const nEdge = Math.floor(n * edge), nFace = n - nEdge;
    const areas = [sx * sy, sx * sy, sx * sz, sx * sz, sy * sz, sy * sz], tot = areas.reduce((a, b) => a + b);
    for (let i = 0; i < nFace; i++) {
      let pick = r() * tot, f = 0; while (pick > areas[f]) { pick -= areas[f]; f++; }
      const a = r() - 0.5, b = r() - 0.5, sgn = f % 2 === 0 ? 0.5 : -0.5; let p;
      if (f < 2) p = [a * sx, b * sy, sgn * sz]; else if (f < 4) p = [a * sx, sgn * sy, b * sz]; else p = [sgn * sx, a * sy, b * sz];
      tgt.push(cx + p[0], cy + p[1], cz + p[2]); kind.push(k);
    }
    for (let i = 0; i < nEdge; i++) {
      const e = Math.floor(r() * 12), a = r() - 0.5, s1 = (e & 1) ? 0.5 : -0.5, s2 = (e & 2) ? 0.5 : -0.5; let p;
      if (e < 4) p = [a * sx, s1 * sy, s2 * sz]; else if (e < 8) p = [s1 * sx, a * sy, s2 * sz]; else p = [s1 * sx, s2 * sy, a * sz];
      tgt.push(cx + p[0], cy + p[1], cz + p[2]); kind.push(k);
    }
  };
  const cyl = (cx, cy, cz, rad, h, n, k = 0) => { for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, top = r() < 0.3; const rr = top ? Math.sqrt(r()) * rad : rad; tgt.push(cx + rr * Math.cos(a), cy + (top ? (r() < 0.5 ? -h / 2 : h / 2) : (r() - 0.5) * h), cz + rr * Math.sin(a)); kind.push(k); } };
  const torus = (cx, cy, cz, R, rr, n, k) => { for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, b = r() * Math.PI * 2; tgt.push(cx + (R + rr * Math.cos(b)) * Math.cos(a), cy + rr * Math.sin(b), cz + (R + rr * Math.cos(b)) * Math.sin(a)); kind.push(k); } };
  // stylised generic full-field digital mammography unit (no brand)
  box(0, -1.78, 0.05, 1.5, 0.16, 1.0, 3500);                  // base plinth
  box(0, -0.25, -0.42, 0.56, 3.0, 0.44, 9000);                // column
  box(0, 0.12, -0.08, 0.36, 2.25, 0.3, 6000);                 // C-arm spine
  box(0, 1.25, 0.32, 0.62, 0.46, 0.86, 7000);                 // x-ray tube housing
  cyl(0, 1.0, 0.52, 0.2, 0.08, 1500);                         // collimator
  box(0, 0.62, 0.74, 0.56, 0.62, 0.02, 2500, 2, 0.5);         // face shield (glass)
  box(0, -0.18, 0.42, 0.74, 0.03, 0.7, 3500, 2, 0.5);         // compression paddle
  box(0, -0.6, 0.4, 0.82, 0.16, 0.8, 6000, 1);                // detector / bucky (pink)
  box(0.0, -0.95, 0.3, 0.3, 0.55, 0.22, 2000);                // detector arm
  box(0.62, 0.2, -0.38, 0.06, 0.5, 0.36, 1600, 2);            // side control screen
  torus(0, -0.6, 0.4, 0.82, 0.012, 2500, 1);                  // scan halo
  torus(0, -1.86, 0.05, 1.35, 0.01, 3000, 3);                 // floor rings
  torus(0, -1.86, 0.05, 1.9, 0.01, 3500, 3);
  torus(0, -1.86, 0.05, 2.5, 0.008, 3500, 3);
  const n = tgt.length, start = new Float32Array(n * 3), delay = new Float32Array(n), seed = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const th = r() * Math.PI * 2, ph = Math.acos(2 * r() - 1), rad = 3.5 + r() * 4;
    start.set([rad * Math.sin(ph) * Math.cos(th), rad * Math.cos(ph) * 0.9 - 1.5, rad * Math.sin(ph) * Math.sin(th)], i * 3);
    delay[i] = 0.12 * r() + 0.3 * clamp((tgt[i * 3 + 1] + 1.9) / 3.6); seed[i] = r();
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(tgt), 3));
  g.setAttribute('aStart', new THREE.BufferAttribute(start, 3));
  g.setAttribute('aDelay', new THREE.BufferAttribute(delay, 1));
  g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  g.setAttribute('aKind', new THREE.BufferAttribute(new Float32Array(kind), 1));
  const m = softPointsMaterial({
    uniforms: { uP: { value: 0 }, uScan: { value: -5 }, uOut: { value: 0 } },
    vertexShader: `uniform float uTime,uP,uScan,uOut,uSize; attribute vec3 aStart; attribute float aDelay,aSeed,aKind; varying vec3 vC; varying float vA;
      void main(){
        float e=clamp((uP-aDelay)/0.55,0.0,1.0); e=e<0.5?4.0*e*e*e:1.0-pow(-2.0*e+2.0,3.0)/2.0;
        vec3 p=mix(aStart,position,e);
        p+= (1.0-e)*vec3(sin(uTime*2.0+aSeed*40.0),cos(uTime*1.7+aSeed*30.0),sin(uTime*1.3+aSeed*20.0))*0.25;
        p+= normalize(position+vec3(0.001,0.5,0.001))*uOut*(1.5+aSeed*3.0);
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
        float d=-mv.z; gl_PointSize=uSize*(aKind>2.5?2.2:2.9)*(10.0/d)*(0.8+aSeed*0.5);
        vec3 gold=vec3(1.0,0.66,0.22); vec3 pk=vec3(1.0,0.08,0.35);
        vec3 c=gold*1.25;
        if(aKind>0.5&&aKind<1.5) c=pk*1.9;
        if(aKind>1.5&&aKind<2.5) c=mix(gold,vec3(1.0),0.35)*0.9;
        if(aKind>2.5) c=gold*0.4;
        float s=exp(-pow((position.y-uScan)*7.0,2.0));
        c+=pk*s*3.2+vec3(1.0)*s*0.8;
        vC=c; vA=(0.35+0.65*e)*(1.0-uOut);
      }`,
    fragmentShader: `uniform float uAlpha; varying vec3 vC; varying float vA;
      void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.08,d); gl_FragColor=vec4(vC*a*vA*uAlpha,1.0);}`,
  });
  const pts = new THREE.Points(g, m); pts.frustumCulled = false; scene.add(pts);
  return pts;
})();

// ---------------------------------------------------------------- Djibouti map
const map = { group: new THREE.Group(), mats: [], pins: [] };
const LON0 = 42.62, LAT0 = 11.8, K = 2.35, KX = K * Math.cos(11.8 * Math.PI / 180);
const proj = (lon, lat) => [(lon - LON0) * KX, (lat - LAT0) * K];
async function makeMap() {
  const coords = await (await fetch('/assets/djibouti.json')).json();
  const shape = new THREE.Shape(coords.map(([lo, la]) => new THREE.Vector2(...proj(lo, la))));
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.12, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.015, bevelSegments: 2 });
  const top = new THREE.MeshStandardMaterial({ color: 0x1a0c13, roughness: 0.7, metalness: 0.1, envMapIntensity: 0.12, emissive: 0x14040b, transparent: true });
  const side = new THREE.MeshPhysicalMaterial({ color: 0xd4a44c, roughness: 0.3, metalness: 1, transparent: true });
  const land = new THREE.Mesh(geo, [top, side]);
  map.group.add(land); map.mats.push(top, side);
  const lineGeo = new THREE.BufferGeometry().setFromPoints(coords.map(([lo, la]) => V(...proj(lo, la), 0.145)));
  const lineMat = new THREE.LineBasicMaterial({ color: new THREE.Color(0xffc861).multiplyScalar(2.4), transparent: true });
  map.group.add(new THREE.Line(lineGeo, lineMat)); map.mats.push(lineMat);
  // sea dot grid
  const dots = [], r = rng(3);
  for (let x = -3.2; x <= 3.2; x += 0.09) for (let y = -3.2; y <= 3.2; y += 0.09) dots.push(x, y, -0.02);
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.Float32BufferAttribute(dots, 3));
  const dm = new THREE.PointsMaterial({ color: new THREE.Color(0x8a6a2e), size: 3, sizeAttenuation: false, transparent: true, opacity: 0.35 });
  map.group.add(new THREE.Points(dg, dm)); map.mats.push(dm);
  // pins (positions indicative within Balbala)
  const bal = proj(43.105, 11.556);
  const defs = [{ id: 'lblH', off: [-0.13, -0.05], col: 0xff2a7a }, { id: 'lblC', off: [0.12, 0.06], col: 0xe3b34c }];
  for (const d of defs) {
    const p = V(bal[0] + d.off[0], bal[1] + d.off[1], 0.14);
    const beamMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(d.col).multiplyScalar(2.2), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.03, 0.9, 12, 1, true), beamMat);
    beam.rotation.x = Math.PI / 2; beam.position.copy(p).add(V(0, 0, 0.45));
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.045, 24, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(d.col).multiplyScalar(3), transparent: true }));
    head.position.copy(p).add(V(0, 0, 0.9));
    const halo = new THREE.Mesh(new THREE.RingGeometry(0.05, 0.065, 48), new THREE.MeshBasicMaterial({ color: new THREE.Color(d.col).multiplyScalar(2.5), transparent: true, side: THREE.DoubleSide, depthWrite: false }));
    halo.position.copy(p);
    map.group.add(beam, head, halo); map.mats.push(beamMat, head.material, halo.material);
    map.pins.push({ ...d, base: p, head, halo, beam });
  }
  map.bal = V(bal[0], bal[1], 0);
  scene.add(map.group);
}

// ---------------------------------------------------------------- Dian K. Pro logo (particles -> crisp plane)
const logo = { y: 0.45, w: 3.3 };
async function makeLogo() {
  const img = await new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.src = '/assets/logo_dkp_mark.png'; });
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const h = logo.w * img.height / img.width; logo.h = h;
  logo.planeMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { map: { value: tex }, uA: { value: 0 }, uSweep: { value: -1 } },
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: `uniform sampler2D map; uniform float uA,uSweep; varying vec2 vUv;
      void main(){ vec4 c=texture2D(map,vUv); vec3 col=pow(c.rgb,vec3(2.2))*1.05;
        float band=exp(-pow((vUv.x+vUv.y*0.45-uSweep)*9.0,2.0)); col+=vec3(1.0,0.85,0.55)*band*2.6*c.a;
        gl_FragColor=vec4(col*c.a*uA, c.a*uA);}`,
  });
  logo.planeMat.premultipliedAlpha = true;
  logo.plane = new THREE.Mesh(new THREE.PlaneGeometry(logo.w, h), logo.planeMat);
  logo.plane.position.set(0, logo.y, 0); scene.add(logo.plane);
  // sample particles
  const cv = document.createElement('canvas'); const sw = 420, sh = Math.round(sw * img.height / img.width);
  cv.width = sw; cv.height = sh; const cx = cv.getContext('2d'); cx.drawImage(img, 0, 0, sw, sh);
  const data = cx.getImageData(0, 0, sw, sh).data, r = rng(11), tgt = [], st = [], dl = [], sd = [];
  for (let y = 0; y < sh; y++) for (let x = 0; x < sw; x++) {
    if (data[(y * sw + x) * 4 + 3] > 120 && r() < 0.85) {
      tgt.push((x / sw - 0.5) * logo.w + (r() - 0.5) * 0.006, logo.y + (0.5 - y / sh) * h, 0);
      const a = r() * Math.PI * 2, rad = 2 + r() * 5;
      st.push(Math.cos(a) * rad, Math.sin(a) * rad * 1.4, -3 + r() * 6); dl.push(r() * 0.35 + 0.25 * (x / sw)); sd.push(r());
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(tgt, 3));
  g.setAttribute('aStart', new THREE.Float32BufferAttribute(st, 3));
  g.setAttribute('aDelay', new THREE.Float32BufferAttribute(dl, 1));
  g.setAttribute('aSeed', new THREE.Float32BufferAttribute(sd, 1));
  logo.pts = new THREE.Points(g, softPointsMaterial({
    uniforms: { uP: { value: 0 } },
    vertexShader: `uniform float uTime,uP,uSize; attribute vec3 aStart; attribute float aDelay,aSeed; varying float vA;
      void main(){ float e=clamp((uP-aDelay)/0.45,0.0,1.0); e=1.0-pow(1.0-e,3.0);
        vec3 p=mix(aStart,position,e)+(1.0-e)*vec3(sin(uTime*3.0+aSeed*50.0),cos(uTime*2.0+aSeed*20.0),0.0)*0.3;
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=uSize*2.6*(12.0/-mv.z); vA=0.4+0.6*e;}`,
    fragmentShader: `uniform float uAlpha; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.05,d);
      gl_FragColor=vec4(vec3(1.0,0.68,0.25)*1.5*a*vA*uAlpha,1.0);}`,
  }));
  logo.pts.frustumCulled = false; scene.add(logo.pts);
}

// ---------------------------------------------------------------- DOM helpers
const $ = (id) => document.getElementById(id);
const els = {};
document.querySelectorAll('[id]').forEach((e) => (els[e.id] = e));
function show(id, t, a, b, { di = 0.55, dout = 0.4, dy = 36, blur = 10, scale = 0 } = {}) {
  const e = els[id]; if (!e) return 0;
  const v = win(t, a, b, di, dout);
  const inP = easeOut(prog(t, a, a + di));
  e.style.opacity = v.toFixed(3);
  const y = (1 - inP) * dy - (prog(t, b - dout, b)) * dy * 0.5;
  const sc = 1 + (1 - inP) * scale;
  e.style.transform = `translateY(${y.toFixed(1)}px) scale(${sc.toFixed(4)})`;
  e.style.filter = v < 0.999 ? `blur(${((1 - v) * blur).toFixed(2)}px)` : 'none';
  return v;
}
function card(id, imgId, sheenId, t, a, b, dir) {
  const v = win(t, a, b, 0.7, 0.5), p = prog(t, a, b);
  const inP = easeOut(prog(t, a, a + 0.9)), outP = easeIn(prog(t, b - 0.5, b));
  const ry = dir * lerp(18, -5, ease(p)) * (1 - 0) + dir * outP * -25;
  const rx = lerp(6, 2, p);
  const ty = (1 - inP) * 140 - outP * 80;
  const sc = lerp(0.9, 1.0, inP) + outP * 0.06;
  els[id].style.opacity = v.toFixed(3);
  els[id].style.transform = `perspective(1900px) translateY(${ty.toFixed(1)}px) rotateY(${ry.toFixed(2)}deg) rotateX(${rx.toFixed(2)}deg) scale(${sc.toFixed(4)})`;
  els[imgId].style.transform = `scale(${lerp(1.02, 1.2, ease(p)).toFixed(4)})`;
  els[sheenId].style.transform = `translateX(${lerp(-120, 120, prog(t, a + 0.4, a + 1.9)).toFixed(1)}%)`;
  return v;
}

// ---------------------------------------------------------------- camera
const camPos = V(), camTgt = V();
function camShot(t, out) {
  // returns [pos, target]
  if (t < 22.0) {
    const z = lerp(12.6, 11.4, ease(prog(t, 0, 5))) + 0.6 * ease(prog(t, 9.6, 10.8)) - 0.5 * ease(prog(t, 10.8, 17));
    const x = Math.sin(t * 0.35) * 0.45;
    const y = 0.1 + 0.25 * ease(prog(t, 4.6, 10));
    out[0].set(x, y, z); out[1].set(0, y * 0.85, 0); return;
  }
  if (t < 30.0) { // mammograph orbit
    const a = lerp(0.75, -0.55, ease(prog(t, 22.2, 27.0)));
    const rr = lerp(9.4, 8.2, ease(prog(t, 22.2, 27)));
    out[0].set(Math.sin(a) * rr, 1.0, Math.cos(a) * rr); out[1].set(0, -0.75, 0); return;
  }
  if (t < 43.2) {
    const a = Math.sin((t - 30) * 0.25) * 0.35;
    const rr = lerp(12.2, 11.0, ease(prog(t, 38.4, 41)));
    out[0].set(Math.sin(a) * rr, 0.1, Math.cos(a) * rr); out[1].set(0, 0.1, 0); return;
  }
  if (t < 46.75) { // map
    const p = ease(prog(t, 43.3, 46.4));
    const tg = V(0.05, 0.12, 0).lerp(map.bal || V(1.1, -0.57, 0), p);
    const d = lerp(13.0, 5.2, p), tilt = lerp(0.55, 0.95, p), yaw = lerp(-0.12, 0.18, p);
    out[1].copy(tg).add(V(0, lerp(-0.6, 0.0, p), 0));
    out[0].set(tg.x + Math.sin(yaw) * d * Math.sin(tilt), tg.y - Math.cos(yaw) * d * Math.sin(tilt), d * Math.cos(tilt)); return;
  }
  const z = lerp(12.4, 12.0, ease(prog(t, 46.6, 58.4)));
  out[0].set(Math.sin(t * 0.3) * 0.25, 0.05, z); out[1].set(0, 0.05, 0);
}
const cuts = [[22.0, 0.9], [30.0, 0.9], [43.2, 0.6], [46.75, 0.45]];
function updateCamera(t) {
  const A = [V(), V()];
  camShot(t, A);
  for (const [c, d] of cuts) {
    if (t > c - d && t < c + d) {
      const B = [V(), V()], w = smooth(prog(t, c - d, c + d));
      if (t < c) { camShot(c + 0.001, B); A[0].lerp(B[0], w); A[1].lerp(B[1], w); }
      else { camShot(c - 0.001, B); B[0].lerp(A[0], w); B[1].lerp(A[1], w); A[0].copy(B[0]); A[1].copy(B[1]); }
    }
  }
  camera.position.copy(A[0]);
  camera.up.set(0, 1, 0);
  camera.lookAt(A[1]);
}

// ---------------------------------------------------------------- frame
const tmpV = V();
function frame(t) {
  updateCamera(t);
  dust.material.uniforms.uTime.value = t;
  dust.material.uniforms.uAlpha.value = 0.55 + 0.45 * win(t, 22, 27, 0.6, 0.6);

  // backdrop mood
  const bu = backdrop.material.uniforms;
  bu.uPink.value = 0.9 - 0.5 * win(t, 43.2, 46.6) ; bu.uGold.value = 0.45 + 0.6 * win(t, 30, 43.2) + 0.8 * win(t, 50.4, 70);
  bu.uPinkPos.value.set(0.5, 0.62 + 0.1 * Math.sin(t * 0.2));

  // sweep light along y
  sweep.intensity = 12; sweep.position.set(1.8 * Math.sin(t * 0.9), 3.5 * Math.sin(t * 0.55), 2.5);

  // ---- 3D title (cover)
  if (title) {
    const out = ease(prog(t, 4.2, 5.2));
    title.visible = out < 1;
    title.position.set(0, 2.32 + out * 0.6, 0.2);
    title.rotation.y = Math.sin(t * 0.6) * 0.06; title.rotation.x = -0.05;
    title.material.opacity = 1 - out;
  }

  // ---- pink ribbon
  {
    let fn = null, opt = {}, vis = 1;
    const twist = (u) => 0.55 * Math.sin(u * 9 + t * 1.3);
    if (t < 10.9) {
      const m = prog(t, 4.6, 6.8);
      const aw = (u, o) => awareness(u, o, 0.95, 0, -0.18).applyAxisAngle(V(0, 1, 0), Math.sin(t * 0.55) * 0.3);
      const sp = (u, o) => serpent(u, o, t, 0, 0.55, 0.0, 10.5, 6.5);
      fn = m <= 0 ? aw : (u, o) => morph(aw, sp, ease(m), u, o);
      vis = 1 - ease(prog(t, 10.0, 10.9));
      opt = { w: vis, twist: m > 0 ? twist : (u) => 0.25 * Math.sin(u * 6 + t), taper: 0.02 };
    } else if (t >= 29.9 && t < 43.6) {
      const gr = easeOut(prog(t, 29.9, 31.1));
      const s1 = (u, o) => serpent(u, o, t, -0.62, 0.32, 0.4, 10, 5.5);
      const c1 = (u, o) => centre(u, o, t);
      const rg = (u, o) => ring(u, o, t, 1.45, 0.2, t * 0.25);
      const m1 = ease(prog(t, 32.8, 35.2)), m2 = ease(prog(t, 38.6, 40.8));
      const f12 = (u, o) => (m1 <= 0 ? s1(u, o) : morph(s1, c1, m1, u, o));
      fn = m2 <= 0 ? f12 : (u, o) => morph(f12, rg, m2, u, o);
      const col = ease(prog(t, 42.75, 43.35));
      if (col > 0) { const f0 = fn; fn = (u, o) => f0(u, o).multiplyScalar(1 - col * 0.98).add(V(0, 0, col * 3)); }
      opt = { u0: 0, u1: m2 > 0.5 ? 1 : gr, w: 1 - col, twist, closed: m2 > 0.98, taper: m2 > 0.98 ? 0 : 0.05 };
      vis = 1;
    } else if (t >= 46.7) {
      const gr = easeOut(prog(t, 46.7, 47.9));
      const sm = ease(prog(t, 50.4, 51.6));
      const s = lerp(0.9, 0.24, sm), cy = lerp(0.12, 2.35, sm);
      fn = (u, o) => awareness(u, o, s, 0, cy).applyAxisAngle(V(0, 1, 0), Math.sin(t * 0.5) * 0.25 * (1 - sm));
      opt = { u0: 0, u1: gr, twist: (u) => 0.3 * Math.sin(u * 7 + t * 1.2), taper: 0.02 };
      pink.width = lerp(0.36, 0.36, sm);
    } else vis = 0;
    if (vis > 0.002 && fn) { pink.update(fn, opt); pink.opacity = 1; } else pink.opacity = 0;
  }

  // ---- gold ribbon
  {
    let fn = null, opt = {}, vis = 0;
    const twist = (u) => 0.5 * Math.sin(u * 8 - t * 1.1);
    if (t >= 30.2 && t < 43.6) {
      const gr = easeOut(prog(t, 30.25, 31.5));
      const s2 = (u, o) => serpent(u, o, t, 0.62, 0.32, Math.PI, 10, 5.5);
      const hx = (u, o) => helixAround(u, o, t, lerp(0.6, 0.4, prog(t, 33, 37)));
      const th = (u, o) => torusHelix(u, o, t, 1.45, 0.2, 0.24, t * 0.25, 6);
      const m1 = ease(prog(t, 32.8, 35.2)), m2 = ease(prog(t, 38.6, 40.8));
      const f12 = (u, o) => (m1 <= 0 ? s2(u, o) : morph(s2, hx, m1, u, o));
      fn = m2 <= 0 ? f12 : (u, o) => morph(f12, th, m2, u, o);
      const col = ease(prog(t, 42.75, 43.35));
      if (col > 0) { const f0 = fn; fn = (u, o) => f0(u, o).multiplyScalar(1 - col * 0.98).add(V(0, 0, col * 3)); }
      opt = { u1: m2 > 0.5 ? 1 : gr, w: 1 - col, twist, closed: m2 > 0.98, taper: m2 > 0.98 ? 0 : 0.05 };
      gold.width = lerp(0.3, 0.13, m2); vis = 1;
    } else if (t >= 46.9) {
      const gr = easeOut(prog(t, 46.9, 48.3));
      const sm = ease(prog(t, 50.4, 51.6));
      const s = lerp(0.9, 0.24, sm), cy = lerp(0.12, 2.35, sm);
      fn = (u, o) => awHelix(u, o, t, s, 0, cy).applyAxisAngle(V(0, 1, 0), Math.sin(t * 0.5) * 0.25 * (1 - sm));
      opt = { u1: gr, twist: () => 0, taper: 0.03 };
      gold.width = lerp(0.075, 0.04, sm); vis = 1;
    }
    if (vis && fn) { gold.update(fn, opt); gold.opacity = 1; } else gold.opacity = 0;
  }

  // ---- filaments (mothers, sisters, daughters)
  {
    const starts = [10.7, 11.6, 13.9];
    fils.forEach((f, i) => {
      if (t < 10.4 || t > 17.9) { f.opacity = 0; return; }
      const gr = easeOut(prog(t, starts[i], starts[i] + 1.3));
      const conv = ease(prog(t, 14.2, 16.4));
      const x0 = lerp([-1.55, 1.55, 0][i], 0, conv), amp = lerp(0.16, 0.38, conv), ph = i * (Math.PI * 2 / 3);
      const fade = 1 - ease(prog(t, 16.9, 17.8));
      f.update((u, o) => serpent(u, o, t * 1.2, x0, amp, ph, 10.5, lerp(5, 6.5, conv)).add(V(0, fade < 1 ? (1 - fade) * 6 : 0, 0)),
        { u1: gr, w: fade, twist: (u) => 0.4 * Math.sin(u * 10 + t * 2 + i) });
      f.opacity = 1;
    });
  }

  // ---- mammograph
  {
    const on = t > 21.6 && t < 28.2;
    mammo.visible = on;
    if (on) {
      const u = mammo.material.uniforms;
      u.uTime.value = t; u.uP.value = lerp(0, 1.0, prog(t, 21.9, 24.0));
      u.uScan.value = lerp(1.6, -1.9, ((t - 24.0) / 1.6) % 1) ; if (t < 24.0) u.uScan.value = -5;
      u.uOut.value = ease(prog(t, 26.7, 27.9));
      u.uAlpha.value = win(t, 21.6, 28.2, 0.4, 0.6);
      mammo.rotation.y = 0.2;
    }
  }

  // ---- map
  if (map.group) {
    const v = win(t, 43.3, 46.8, 0.6, 0.4);
    map.group.visible = v > 0.003;
    if (map.group.visible) {
      const rise = easeOut(prog(t, 43.3, 44.2));
      map.group.position.set(0, 0, (1 - rise) * -1.5);
      map.mats.forEach((m) => (m.opacity = v));
      map.pins.forEach((p, i) => {
        const pv = easeOut(prog(t, 44.0 + i * 0.35, 44.7 + i * 0.35));
        p.beam.scale.set(1, Math.max(pv, 0.001), 1); p.beam.position.copy(p.base).add(V(0, 0, 0.45 * pv));
        p.head.position.copy(p.base).add(V(0, 0, 0.9 * pv)); p.head.visible = pv > 0.05;
        const pulse = ((t * 0.9 + i * 0.5) % 1);
        p.halo.scale.setScalar(1 + pulse * 5); p.halo.material.opacity = v * (1 - pulse) * pv;
        // DOM label
        tmpV.copy(p.head.position).applyMatrix4(map.group.matrixWorld);
        map.group.updateMatrixWorld(); camera.updateMatrixWorld();
        tmpV.copy(p.head.position); map.group.localToWorld(tmpV); tmpV.project(camera);
        const x = (tmpV.x * 0.5 + 0.5) * W, y = (-tmpV.y * 0.5 + 0.5) * H;
        const lv = Math.min(v, easeOut(prog(t, 44.5 + i * 0.35, 45.1 + i * 0.35)));
        const el = els[p.id];
        el.style.opacity = lv.toFixed(3);
        const lx = i === 0 ? x - 120 : x + 130, ly = i === 0 ? y + 190 : y - 40;
        el.style.left = `${clamp(lx, 250, 830).toFixed(1)}px`; el.style.top = `${clamp(ly, 640, 1290).toFixed(1)}px`;
      });
    }
  }

  // ---- logo
  if (logo.pts) {
    const p = prog(t, 50.5, 52.9);
    logo.pts.visible = t > 50.3 && t < 54.0;
    logo.pts.material.uniforms.uP.value = p; logo.pts.material.uniforms.uTime.value = t;
    logo.pts.material.uniforms.uAlpha.value = (1 - ease(prog(t, 52.6, 53.6))) * easeOut(prog(t, 50.3, 50.8));
    logo.planeMat.uniforms.uA.value = ease(prog(t, 52.4, 53.4));
    logo.planeMat.uniforms.uSweep.value = lerp(-0.6, 2.0, prog(t, 53.3, 54.8));
    logo.plane.visible = t > 52.3;
  }

  // ---- DOM layers
  const dom = (id, a, b, o) => show(id, t, a, b, o);
  els.scrimTop.style.opacity = (0.75 + 0.25 * win(t, 17, 30) - 0.65 * (1 - ease(prog(t, 4.2, 5.2)))).toFixed(3);
  els.scrimBot.style.opacity = (0.9).toFixed(3);
  // A
  dom('a0', -1, 4.6, { dout: 0.5 });
  dom('a1', -1, 4.8, { dout: 0.5 });
  dom('h1', 5.25, 10.4); dom('h2', 7.6, 10.4); dom('h3', 9.1, 10.6, { scale: 0.08 });
  // B
  dom('b1', 11.0, 14.35, { scale: 0.1 }); dom('b2', 11.85, 14.35, { scale: 0.1 }); dom('b3', 12.55, 14.35, { scale: 0.1 }); dom('b4', 12.95, 14.35);
  dom('b5', 14.4, 17.3); dom('b6', 15.85, 17.3, { scale: 0.06 });
  // C
  els.bgH.style.opacity = (0.75 * win(t, 17.2, 22.6, 0.8, 0.6)).toFixed(3);
  card('cardH', 'imgH', 'sheenH', t, 17.3, 22.55, 1);
  dom('c1', 17.55, 22.4); dom('c2', 18.95, 22.4); dom('c3', 19.25, 22.4, { scale: 0.06 }); dom('c4', 19.7, 22.4); dom('c5', 21.2, 22.4);
  // D
  dom('d1', 22.5, 26.75); dom('d2', 24.55, 26.75, { scale: 0.06 }); dom('d3', 25.35, 26.75);
  // E
  els.bgC.style.opacity = (0.75 * win(t, 26.6, 30.3, 0.8, 0.6)).toFixed(3);
  card('cardC', 'imgC', 'sheenC', t, 26.7, 30.25, -1);
  dom('e0', 26.75, 30.15); dom('e2', 26.85, 30.15); dom('e3', 28.45, 30.15, { scale: 0.06 }); dom('e4', 29.0, 30.15);
  // F
  dom('f1', 30.15, 32.85, { scale: 0.08 }); dom('f2', 31.15, 32.85, { scale: 0.08 }); dom('f3', 31.6, 32.85, { scale: 0.08 });
  dom('f4', 32.85, 43.0);
  dom('f5', 32.85, 35.6); dom('f6', 33.5, 35.6);
  dom('f7', 35.65, 38.65); dom('f8', 36.4, 38.65);
  dom('f9', 38.7, 43.1); dom('f10', 41.4, 43.1);
  // G
  dom('g1', 43.35, 46.4); dom('g2', 43.5, 46.4); dom('g3', 44.3, 46.45, { dy: 60 });
  if (!map.group.visible) { els.lblH.style.opacity = 0; els.lblC.style.opacity = 0; }
  // H
  dom('hA', 46.55, 50.5); dom('hB', 47.5, 50.5);
  if (SHOW_PARTNERS) { dom('hC', 47.0, 50.45); dom('partners', 47.25, 50.45, { dy: 50 }); }
  else { dom('hC', 47.0, 50.45, { dy: 0 }); els.hC.style.top = '1440px'; els.partners.style.opacity = 0; }
  // I
  dom('iA', 52.9, 99, { blur: 6 });
  dom('iB', 54.1, 99, { blur: 8 });
  dom('iC', 55.2, 99, { blur: 6 });
  // tiny flash on the beat transitions
  const fl = Math.max(0, 1 - Math.abs(t - 10.6) / 0.25) * 0.18 + Math.max(0, 1 - Math.abs(t - 43.5) / 0.25) * 0.15 + Math.max(0, 1 - Math.abs(t - 52.9) / 0.3) * 0.1;
  els.flash.style.opacity = fl.toFixed(3);

  bloom.strength = 0.5 + 0.3 * win(t, 22, 27) + 0.15 * win(t, 50.5, 54);
  composer.render();
}

window.renderAt = (t) => { frame(t); return true; };
(async () => {
  await Promise.all([makeTitle(), makeMap(), makeLogo(), document.fonts.ready,
    ...[...document.images].map((i) => (i.complete ? 1 : new Promise((r) => (i.onload = i.onerror = r))))]);
  await document.fonts.load('700 80px "Playfair Display"'); await document.fonts.load('600 italic 80px "Playfair Display"');
  await document.fonts.load('600 40px Inter'); await document.fonts.load('700 40px Inter'); await document.fonts.load('500 40px Inter');
  frame(0);
  window.__ready = true;
})();
