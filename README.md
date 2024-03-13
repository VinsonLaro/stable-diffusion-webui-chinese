# Stable Diffusion WebUI Chinese 0313

[![](https://img.shields.io/badge/汉化-B站主页-purple)](https://space.bilibili.com/22970812)
[![](https://img.shields.io/badge/汉化-视频教程-purple)](https://www.bilibili.com/video/BV1kg4y1H73b)
[![](https://img.shields.io/badge/汉化-QQ交流群-purple)](https://jq.qq.com/?_wv=1027&k=wEbRm1eU)

## 解释说明

此项目为[Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)简体中文扩展

当前版本为0313，即基于官方webui和自用插件的本地化模板，于2024年3月13日之前的最新版本进行的汉化。

本人精力有限不可能每个功能都体验过，然后根据具体功能来翻译，所以有翻译得不对或者更好的翻译请联系我。

翻译结果来自chatGPT、有道翻译和网络检索。

## 包含以下扩展翻译

[ControlNet](https://github.com/Mikubill/sd-webui-controlnet)
版本：aa2aa812		2024-03-06 10:52:19	

[openpose-editor](https://github.com/huchenlei/sd-webui-openpose-editor)
版本：cebe13e0	2023-12-19 11:58:26

[multidiffusion-upscaler](https://github.com/pkuliyi2015/multidiffusion-upscaler-for-automatic1111)
版本：76cde3c2		2024-03-09 15:38:00

[artists-to-study](https://github.com/camenduru/stable-diffusion-webui-artists-to-study)
版本：5cd19f68 (Mon Jun 26 08:38:08 2023)

[dataset-tag-editor](https://github.com/toshiaki1729/stable-diffusion-webui-dataset-tag-editor)
版本：7a2f4c53 (Mon Jun 5 10:12:00 2023)

[lora-block-weight](https://github.com/hako-mikan/sd-webui-lora-block-weight)
版本：1fa7eb78		2024-02-12 22:56:37	

[segment-anything](https://github.com/continue-revolution/sd-webui-segment-anything)
版本：982138cf		2024-02-24 04:25:02

[vectorstudio](https://github.com/GeorgLegato/stable-diffusion-webui-vectorstudio)
版本：03535f64		2023-05-28 22:27:48	

[posex](https://github.com/hnmr293/posex)
版本：292f92d5		2023-05-03 16:59:57

## 安装说明

### 方法1：通过WebUI拓展进行安装

1.打开stable diffusion webui，进入"Extensions"选项卡

2.点击"Install from URL"，注意"URL for extension's git repository"下方的输入框

3.粘贴或输入本Git仓库地址`https://github.com/VinsonLaro/stable-diffusion-webui-chinese`

4.点击下方的黄色按钮"Install"即可完成安装，然后重启WebUI(点击"Install from URL"左方的"Installed"，然后点击黄色按钮"Apply and restart UI"网页下方的"Reload UI"完成重启)

5.点击"Settings"，左侧点击"User interface"界面，在界面里最下方的"Localization (requires restart)"，选择"Chinese-All"或者"Chinese-English"

6.点击界面最上方的黄色按钮"Apply settings"，再点击右侧的"Reload UI"即可完成汉化

### 方法2：直接复制翻译好的本地化模板

1.在任意目录下使用`git clone https://github.com/VinsonLaro/stable-diffusion-webui-chinese`

2.进入下载好的文件夹,把"localizations"文件夹内的"Chinese-All.json"和"Chinese-English.json"复制到"stable-diffusion-webui\localizations"目录下

3.点击"Settings"，左侧点击"User interface"界面，在界面里最下方的"Localization (requires restart)"，选择"Chinese-All"或者"Chinese-English"

4.点击界面最上方的黄色按钮"Apply settings"，再点击右侧的"Reload UI"即可完成汉化

## 其他

自从开始玩AI绘画，一晃眼都过去快2年了。由于个人工作和懒惰的原因，23年10月更新以后今天(3月)才有空更新。

从一开始的disco diffusion到stable diffusion，从SD1.5和waifu1.4，再到novelai泄露带来的爆火，还有lora以及controlnet的大规模应用和comfyUI的出现。AI绘画也算是摆脱了鬼图，逐渐可用商用，走进了大众的视野。

去年年末以后我更关注的是LLM，自己和团队也在开发LLM相关的项目。对AI绘画这边的关注逐渐变少，之前C站上的每一个新出的lora我都会看过，我觉得优质lora都会点like，后面游戏公司裁员以后忙于生计以及个人电脑限制，启动SD的次数越来越少。

个人觉得AI绘画的增速变慢，很难再出现像上面每个事件，都能让AI绘画上一新台阶的事情了。

希望AGI早日实现。

# Star History

[![Star History](https://api.star-history.com/svg?repos=VinsonLaro/stable-diffusion-webui-chinese&Date&type=Date)](https://star-history.com/#VinsonLaro/stable-diffusion-webui-chinese&Date)