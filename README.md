# Stable Diffusion WebUI Chinese 0220

[![](https://img.shields.io/badge/汉化-B站主页-purple)](https://space.bilibili.com/22970812)
[![](https://img.shields.io/badge/汉化-QQ交流群-purple)](https://jq.qq.com/?_wv=1027&k=wEbRm1eU)

## 解释说明

此项目为[Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)简体中文扩展

当前版本为0220，即基于官方webui和自用插件的本地化模板，于2月20日之前的最新版本进行的汉化。


## 包含以下扩展翻译

[ControlNet](https://github.com/Mikubill/sd-webui-controlnet)


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