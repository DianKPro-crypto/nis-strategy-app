// Lumière dorée sous le pointeur : un halo doux qui suit la souris ou le doigt,
// et un seul anneau d'or par pression, disparu en moins d'une seconde.
import {
  abs,
  clamp,
  exp,
  length,
  mix,
  picture,
  pointers,
  scene,
  shader,
  smoothstep,
  still,
  vec2,
  vec3,
  vec4,
} from 'claude-code/shader'

const GOLD = vec3(0.89, 0.7, 0.3)

export default shader({
  fps: 30,
  passes: [
    picture(p => {
      const base = scene.sample(p.uv)
      let glow = 0

      for (const q of pointers) {
        const d = length(vec2(p.point - q.at))
        const present = clamp(q.age * 3, 0, 1) * (1 - clamp(q.gone * 2, 0, 1))

        // Halo qui suit le pointeur
        glow = glow + exp((-d * d) / (2 * 110 * 110)) * 0.22 * present

        // Un anneau par pression, étroit, qui s'éteint avant une seconde
        const r = q.age * 380
        const ring = smoothstep(12, 0, abs(d - r)) * (1 - smoothstep(0.05, 0.85, q.age))
        glow = glow + ring * 0.4 * q.down
      }

      const amount = clamp(glow, 0, 0.55) * (1 - still)
      return vec4(mix(base.rgb, GOLD, amount), base.a)
    }),
  ],
})
