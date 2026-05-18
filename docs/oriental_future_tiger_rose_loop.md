# 东方未来主义循环视频：心有猛虎，细嗅蔷薇

本文件是 AI Video Studio 的高质量循环视频任务包，用于制作一段约 3 分钟、由 10–15 秒高质量基础循环无缝延展而成的东方未来主义动画视频。

> 质量原则：不要把 CPU mock 或程序化预览当作最终片。正式成片应先由真实视频生成模型产出高质感 10–15 秒母版，再用仓库脚本无损倾向地延展到 180 秒。

## 1. 核心目标

主题意境：心有猛虎，细嗅蔷薇。

画面需要同时呈现两种气质：

- 内在刚猛：东方猛虎、稳定气场、克制力量、深沉洞察。
- 外在温柔：蔷薇、微风、花香粒子、呼吸感、柔和光影。

最终成片应像一幅会呼吸的东方未来意境图：安静、强大、温柔、明亮，兼具中国传统神韵与科技想象力。

## 2. 高质量成片规格

| 项目 | 高质量建议 |
|---|---|
| 最终时长 | 180 秒 |
| 基础循环母版 | 12 秒，必须首尾自然衔接 |
| 帧率 | 30 fps；电影感可 24 fps |
| 比例 | 16:9；动态壁纸可另出 9:16 |
| 母版分辨率 | 1920×1080 起步；优先 4K |
| 最终分辨率 | 3840×2160 优先；空间不足时 1920×1080 |
| 镜头 | 单镜头慢推或极轻微环绕，禁止快速切换 |
| 循环锚点 | 虎的呼吸、胡须、蔷薇摆动、池水涟漪、光粒流动、霞光明灭 |
| 禁止项 | 字幕、片头、片尾、水印、logo、印章、标题、任何可读文字 |

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

## 5. 高质量推荐流程

### Step 1：生成 12 秒高质量无缝循环母版

优先使用真实视频模型或 ComfyUI 视频工作流，不建议用 mock。关键设置：

```text
Duration: 12s
FPS: 24 or 30
Resolution: 1920x1080 minimum, 3840x2160 preferred
Camera: slow_push_in or subtle_orbit
Loop: enabled / seamless / first-last frame consistent
Text / watermark / logo: disabled
Prompt adherence: high
Motion strength: low to medium-low
Temporal consistency: high
```

若模型支持首尾帧：

1. 先生成一张 4K 主视觉静帧。
2. 将同一张静帧同时作为 first frame 与 last frame。
3. 中间只做轻微呼吸、花瓣、粒子、水波、雾气与极慢镜头运动。
4. 这样最容易得到无缝循环。

### Step 2：质检 12 秒母版

重点检查：

- 虎的身体、眼睛、毛发、条纹是否稳定。
- 蔷薇花瓣是否破碎或跳变。
- 是否误生成文字、水印、logo、印章、符号、数字或图腾。
- 首尾帧光线、粒子、花瓣、水波、雾气是否能自然接上。
- 是否过曝、过饱和、廉价霓虹、赛博噪声过重。

### Step 3：用仓库脚本高质量延展到 3 分钟

将高质量母版放入：

```text
data/assets/oriental_future_tiger_rose_12s_master.mp4
```

生成 4K 高质量 180 秒版本：

```bash
python scripts/extend_seamless_loop_hq.py \
  data/assets/oriental_future_tiger_rose_12s_master.mp4 \
  --output data/outputs/oriental_future_tiger_rose_180s_4k_hq.mp4 \
  --duration 180 \
  --fps 30 \
  --width 3840 \
  --crf 14 \
  --preset slow
```

生成 1080p 高质量版本：

```bash
python scripts/extend_seamless_loop_hq.py \
  data/assets/oriental_future_tiger_rose_12s_master.mp4 \
  --output data/outputs/oriental_future_tiger_rose_180s_1080p_hq.mp4 \
  --duration 180 \
  --fps 30 \
  --width 1920 \
  --crf 14 \
  --preset slow
```

说明：`--crf 12–16` 属于高质量范围，数值越低文件越大。`--preset veryslow` 质量/压缩率更好，但耗时更长。

### Step 4：可选高质量后处理

如需要更细腻，可在外部工具中做：

- Topaz Video AI / DaVinci Resolve：降噪、锐化、4K 放大、帧稳定。
- FFmpeg：轻微锐化、色彩空间规范化、码率控制。
- ComfyUI：视频超分、去闪烁、帧间一致性增强。

不要添加字幕、片头、片尾、logo、水印或任何文字层。

## 6. 仅用于构图预览的 CPU 脚本

仓库里的 `scripts/render_oriental_future_tiger_rose_loop.py` 只用于快速预览构图、色彩和循环节奏，不作为最终高质量成片。确需预览时可运行：

```bash
python scripts/render_oriental_future_tiger_rose_loop.py \
  --seconds 12 \
  --loop-seconds 12 \
  --fps 24 \
  --resolution 1920x1080 \
  --output data/outputs/oriental_future_tiger_rose_preview_12s.mp4
```

## 7. 质量检查清单

- [ ] 没有任何中英文文字、标题、印章、水印、logo、二维码或可读信息。
- [ ] 没有人头像或人物全身。
- [ ] 猛虎安静伏踞，不攻击、不咆哮、不捕猎。
- [ ] 毛发、虎纹、眼睛、鼻尖气流、胡须、耳朵动作稳定可信。
- [ ] 蔷薇具备轻柔生命感、微光与香气流线。
- [ ] 九紫离火元素自然隐喻化，不出现数字 9 或直白图腾。
- [ ] 镜头连续、缓慢、稳定，无突兀切换。
- [ ] 12 秒基础段首尾衔接自然，可重复至 3 分钟。
- [ ] 色彩高级、清透、低噪声、不过曝、不过饱和。
- [ ] 最终 180 秒成片不应出现明显重复顿挫或压缩块。