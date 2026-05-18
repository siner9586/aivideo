# 东方未来主义循环视频：心有猛虎，细嗅蔷薇

本文件为 AI Video Studio 的高质感循环视频任务包，用于制作一段约 3 分钟、由 10–15 秒基础循环无缝延展而成的东方未来主义动画视频。

## 1. 核心目标

主题意境：心有猛虎，细嗅蔷薇。

画面需要同时呈现两种气质：

- 内在刚猛：东方猛虎、稳定气场、克制力量、深沉洞察。
- 外在温柔：蔷薇、微风、花香粒子、呼吸感、柔和光影。

最终成片应像一幅会呼吸的东方未来意境图：安静、强大、温柔、明亮，兼具中国传统神韵与科技想象力。

## 2. 推荐视频规格

| 项目 | 建议值 |
|---|---|
| 最终时长 | 180 秒 |
| 基础循环 | 12 秒，重复 15 次 |
| 帧率 | 24 fps 或 30 fps |
| 比例 | 16:9；动态壁纸可另出 9:16 |
| 分辨率 | 1920×1080 起步；正式版建议 4K |
| 镜头 | 单镜头慢推或极轻微环绕，禁止快速切换 |
| 循环锚点 | 虎的呼吸、胡须、蔷薇摆动、池水涟漪、光粒流动、霞光明灭 |

## 3. Master Prompt

Create a seamless looping high-end oriental futurism cinematic animation, about 12 seconds as the base loop and extendable to 3 minutes. No human face, no human body, no readable Chinese or English text, no title, no seal, no watermark, no logo, no symbolic bagua diagram, no readable information.

The core image is an elegant eastern tiger resting quietly in an oriental future courtyard. The tiger is not attacking, not roaring, not hunting. It crouches with calm strength, smooth muscles, stable posture, deep observant eyes, and slow breathing. The tiger lowers its head slightly toward a blooming rose and gently smells it, expressing the spirit of “strength and tenderness coexisting, sharpness and restraint held together.” Fur must be extremely detailed and realistic, with subtle movement from wind and breathing; whiskers tremble gently, ears rotate occasionally, eyes blink very rarely and calmly. Tiger stripes may contain extremely fine gold and purple-gold energy filaments, naturally blending ancient cloud thunder patterns, geometric Huiwen patterns, and future nano-circuitry; these lines pulse faintly with the breathing rhythm.

The rose is a single luminous futuristic rose, soft and alive. Petals unfold in pale pink, rose red, crimson, purple and warm gold gradients, with subtle biological glow on the edges. The stem sways gently in the breeze; petals tremble slowly; one or two petals drift through the air in graceful paths. Around the rose, delicate particles and fragrance-like translucent flow lines expand softly, as if scent, emotion, inspiration and energy move through the air. When the tiger approaches the rose, show a very subtle airflow disturbance and particle spiral near the nose.

The environment is a fusion of Chinese classical courtyard and future technology space: pavilion, moon gate, flying eaves, corridor, scholar rocks, pine branches, mirror-like pond, jade steps, translucent screens, cloud motifs, mist and distant mountain silhouettes. Materials should be futuristic: dark brushed metal, translucent jade, crystal, glass, optical fiber texture, restrained gilded structures. Background holographic curtains, suspended crystals, fine light bands, slow data particles, subtle star tracks and energy arcs may appear, but must remain elegant, clean and restrained, not noisy cyberpunk.

Composition should follow an orderly oriental spatial rhythm: stable central axis, balanced sides, layered depth, solid and void coexisting. The tiger and rose form the central visual core. The upper and southern region carries a gentle Li-fire atmosphere: purple-red dawn glow, warm golden solar halo, abstract phoenix-feather light, subtle fire-pattern energy layers, red-jade lantern light, and almost invisible vermilion-bird-like glimmer. These must remain atmospheric, not become separate creatures. The lower and northern region contains calm mirror water to balance the fire, like quiet water running deep. The left / eastern side uses pine, bamboo shadow and jade green vitality; the right / western side uses moon-white stone steps, pale-gold vessels or crystals to gather and balance the field.

Nine-purple Li-fire symbolism must be natural and implicit: civilization, inspiration, reputation, propagation, aesthetics, warmth, light and spiritual ascent. Use purple, crimson, rose red, warm gold, gilded gold, warm white and deep ink green, with restrained jade green and moon white. In the southern sky, include soft purple-gold haze and nine barely perceptible warm light points, expressed as distant lamps, flower-shaped bokeh, crystal refractions, particle clusters or nine-petal radiance. Do not show the number 9 and do not make it a blunt symbol.

Camera language: elegant, slow, breathing. Use a slow push-in or very subtle orbit, with delicate parallax among foreground flowers, tiger, rose, water and background architecture. No sudden cuts, no fast pan, no shaky movement, no dizziness. The loop point must be invisible, using wind, petals, particles, breathing, water ripples and background glow as loop anchors.

Lighting: cinematic, layered, clear and restrained. Main light comes from upper southern warm gold and purple-red compound light, outlining the tiger, rose petals and courtyard structures. Fill light comes from water reflection, ground glow, crystal refraction and ambient scattering. Use volumetric light, mist diffusion, rim highlights and soft backlight. Fur highlights and shadows must feel natural; translucent rose petals should glow gently. Overall feeling: light but not dazzling, warm but not dry, stillness with power, softness with hidden edge.

Style: oriental futurism, believable surrealism, premium digital art, cinematic composition, 8K texture, ultra detailed, deep spatial layers, refined low-saturation colors, delicate particles, realistic fur and petals, Chinese landscape atmosphere blended with future civilization.

## 4. Negative Prompt

human face, human body, portrait, cartoon, chibi, children illustration, horror, brutal hunting, roar, attack, blood, gore, ruin, mech battle, cheap cyberpunk, dense neon signs, readable text, Chinese text, English text, title, subtitle, seal, watermark, logo, symbol, QR code, bagua diagram, talisman, religious ritual, creepy occult, over-mysticism, cluttered composition, low resolution, flickering noise, fast camera movement, abrupt cut, visible loop break, overexposure, oversaturation, harsh contrast, cheap glow outline, dirty lens flare, distorted tiger anatomy, extra limbs, deformed face, plastic fur, artificial petals.

## 5. 推荐生成流程

### A. 正式高质感路线

1. 用上方 Master Prompt 生成 12 秒基础循环。优先使用支持视频循环、首尾帧控制或参考帧一致性的后端，例如 Seedance、即梦、Runway、Kling、ComfyUI 视频工作流、Wan / CogVideoX / Hunyuan / LTX 等。
2. 若平台不支持 180 秒，先产出 12 秒无缝循环段，再在 AI Video Studio 的后处理/合成链路中重复 15 次。
3. 使用质量评估面板重点检查：闪烁、循环断点、虎纹漂移、毛发破碎、花瓣跳帧、背景文字/符号误生成。
4. 导出时关闭字幕、片头、片尾、logo、水印或任何文字层。

### B. 仓库内 CPU-only 概念预览路线

使用 `scripts/render_oriental_future_tiger_rose_loop.py` 生成无文字的程序化概念预览：

```bash
python scripts/render_oriental_future_tiger_rose_loop.py --seconds 180 --loop-seconds 12 --fps 24 --resolution 1280x720
```

输出：

```text
data/outputs/oriental_future_tiger_rose_loop.mp4
```

该脚本用于本地预览构图、节奏、循环锚点和颜色关系，不替代真实视频生成模型的毛发、花瓣与电影级写实能力。

## 6. 质量检查清单

- [ ] 没有任何中英文文字、标题、印章、水印、logo、二维码或可读信息。
- [ ] 没有人头像或人物全身。
- [ ] 猛虎安静伏踞，不攻击、不咆哮、不捕猎。
- [ ] 蔷薇具备轻柔生命感、微光与香气流线。
- [ ] 九紫离火元素自然隐喻化，不出现数字 9 或直白图腾。
- [ ] 镜头连续、缓慢、稳定，无突兀切换。
- [ ] 12 秒基础段首尾衔接自然，可重复至 3 分钟。
- [ ] 色彩高级、清透、低噪声、不过曝、不过饱和。
