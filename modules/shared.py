import argparse
import datetime
import json
import os
import sys

import gradio as gr
import tqdm

import modules.artists
import modules.interrogate
import modules.memmon
import modules.sd_models
import modules.styles
import modules.devices as devices
from modules import sd_samplers, hypernetwork
from modules.paths import models_path, script_path, sd_path

sd_model_file = os.path.join(script_path, 'model.ckpt')
default_sd_model_file = sd_model_file
parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, default=os.path.join(sd_path, "configs/stable-diffusion/v1-inference.yaml"), help="path to config which constructs model",)
parser.add_argument("--ckpt", type=str, default=sd_model_file, help="path to checkpoint of stable diffusion model; if specified, this checkpoint will be added to the list of checkpoints and loaded",)
parser.add_argument("--ckpt-dir", type=str, default=None, help="Path to directory with stable diffusion checkpoints")
parser.add_argument("--gfpgan-dir", type=str, help="GFPGAN directory", default=('./src/gfpgan' if os.path.exists('./src/gfpgan') else './GFPGAN'))
parser.add_argument("--gfpgan-model", type=str, help="GFPGAN model file name", default=None)
parser.add_argument("--no-half", action='store_true', help="do not switch the model to 16-bit floats")
parser.add_argument("--no-half-vae", action='store_true', help="do not switch the VAE model to 16-bit floats")
parser.add_argument("--no-progressbar-hiding", action='store_true', help="do not hide progressbar in gradio UI (we hide it because it slows down ML if you have hardware acceleration in browser)")
parser.add_argument("--max-batch-count", type=int, default=16, help="maximum batch count value for the UI")
parser.add_argument("--embeddings-dir", type=str, default=os.path.join(script_path, 'embeddings'), help="embeddings directory for textual inversion (default: embeddings)")
parser.add_argument("--allow-code", action='store_true', help="allow custom script execution from webui")
parser.add_argument("--medvram", action='store_true', help="enable stable diffusion model optimizations for sacrificing a little speed for low VRM usage")
parser.add_argument("--lowvram", action='store_true', help="enable stable diffusion model optimizations for sacrificing a lot of speed for very low VRM usage")
parser.add_argument("--always-batch-cond-uncond", action='store_true', help="disables cond/uncond batching that is enabled to save memory with --medvram or --lowvram")
parser.add_argument("--unload-gfpgan", action='store_true', help="does not do anything.")
parser.add_argument("--precision", type=str, help="evaluate at this precision", choices=["full", "autocast"], default="autocast")
parser.add_argument("--share", action='store_true', help="use share=True for gradio and make the UI accessible through their site (doesn't work for me but you might have better luck)")
parser.add_argument("--codeformer-models-path", type=str, help="Path to directory with codeformer model file(s).", default=os.path.join(models_path, 'Codeformer'))
parser.add_argument("--gfpgan-models-path", type=str, help="Path to directory with GFPGAN model file(s).", default=os.path.join(models_path, 'GFPGAN'))
parser.add_argument("--esrgan-models-path", type=str, help="Path to directory with ESRGAN model file(s).", default=os.path.join(models_path, 'ESRGAN'))
parser.add_argument("--bsrgan-models-path", type=str, help="Path to directory with BSRGAN model file(s).", default=os.path.join(models_path, 'BSRGAN'))
parser.add_argument("--realesrgan-models-path", type=str, help="Path to directory with RealESRGAN model file(s).", default=os.path.join(models_path, 'RealESRGAN'))
parser.add_argument("--scunet-models-path", type=str, help="Path to directory with ScuNET model file(s).", default=os.path.join(models_path, 'ScuNET'))
parser.add_argument("--swinir-models-path", type=str, help="Path to directory with SwinIR model file(s).", default=os.path.join(models_path, 'SwinIR'))
parser.add_argument("--ldsr-models-path", type=str, help="Path to directory with LDSR model file(s).", default=os.path.join(models_path, 'LDSR'))
parser.add_argument("--xformers", action='store_true', help="enable xformers for cross attention layers")
parser.add_argument("--force-enable-xformers", action='store_true', help="enable xformers for cross attention layers regardless of whether the checking code thinks you can run it; do not make bug reports if this fails to work")
parser.add_argument("--deepdanbooru", action='store_true', help="enable deepdanbooru interrogator")
parser.add_argument("--opt-split-attention", action='store_true', help="force-enables cross-attention layer optimization. By default, it's on for torch.cuda and off for other torch devices.")
parser.add_argument("--disable-opt-split-attention", action='store_true', help="force-disables cross-attention layer optimization")
parser.add_argument("--opt-split-attention-v1", action='store_true', help="enable older version of split attention optimization that does not consume all the VRAM it can find")
parser.add_argument("--use-cpu", nargs='+',choices=['SD', 'GFPGAN', 'BSRGAN', 'ESRGAN', 'SCUNet', 'CodeFormer'], help="use CPU as torch device for specified modules", default=[])
parser.add_argument("--listen", action='store_true', help="launch gradio with 0.0.0.0 as server name, allowing to respond to network requests")
parser.add_argument("--port", type=int, help="launch gradio with given server port, you need root/admin rights for ports < 1024, defaults to 7860 if available", default=None)
parser.add_argument("--show-negative-prompt", action='store_true', help="does not do anything", default=False)
parser.add_argument("--ui-config-file", type=str, help="filename to use for ui configuration", default=os.path.join(script_path, 'ui-config.json'))
parser.add_argument("--hide-ui-dir-config", action='store_true', help="hide directory configuration from webui", default=False)
parser.add_argument("--ui-settings-file", type=str, help="filename to use for ui settings", default=os.path.join(script_path, 'config.json'))
parser.add_argument("--gradio-debug",  action='store_true', help="launch gradio with --debug option")
parser.add_argument("--gradio-auth", type=str, help='set gradio authentication like "username:password"; or comma-delimit multiple like "u1:p1,u2:p2,u3:p3"', default=None)
parser.add_argument("--gradio-img2img-tool", type=str, help='gradio image uploader tool: can be either editor for ctopping, or color-sketch for drawing', choices=["color-sketch", "editor"], default="editor")
parser.add_argument("--opt-channelslast", action='store_true', help="change memory type for stable diffusion to channels last")
parser.add_argument("--styles-file", type=str, help="filename to use for styles", default=os.path.join(script_path, 'styles.csv'))
parser.add_argument("--autolaunch", action='store_true', help="open the webui URL in the system's default browser upon launch", default=False)
parser.add_argument("--use-textbox-seed", action='store_true', help="use textbox for seeds in UI (no up/down, but possible to input long seeds)", default=False)
parser.add_argument("--disable-console-progressbars", action='store_true', help="do not output progressbars to console", default=False)
parser.add_argument("--enable-console-prompts", action='store_true', help="print prompts to console when generating with txt2img and img2img", default=False)
parser.add_argument('--vae-path', type=str, help='Path to Variational Autoencoders model', default=None)
parser.add_argument("--disable-safe-unpickle", action='store_true', help="disable checking pytorch models for malicious code", default=False)


cmd_opts = parser.parse_args()

devices.device, devices.device_gfpgan, devices.device_bsrgan, devices.device_esrgan, devices.device_scunet, devices.device_codeformer = \
(devices.cpu if x in cmd_opts.use_cpu else devices.get_optimal_device() for x in ['SD', 'GFPGAN', 'BSRGAN', 'ESRGAN', 'SCUNet', 'CodeFormer'])

device = devices.device

batch_cond_uncond = cmd_opts.always_batch_cond_uncond or not (cmd_opts.lowvram or cmd_opts.medvram)
parallel_processing_allowed = not cmd_opts.lowvram and not cmd_opts.medvram
xformers_available = False
config_filename = cmd_opts.ui_settings_file

hypernetworks = hypernetwork.list_hypernetworks(os.path.join(models_path, 'hypernetworks'))
loaded_hypernetwork = None


class State:
    skipped = False
    interrupted = False
    job = ""
    job_no = 0
    job_count = 0
    job_timestamp = '0'
    sampling_step = 0
    sampling_steps = 0
    current_latent = None
    current_image = None
    current_image_sampling_step = 0
    textinfo = None

    def skip(self):
        self.skipped = True

    def interrupt(self):
        self.interrupted = True

    def nextjob(self):
        self.job_no += 1
        self.sampling_step = 0
        self.current_image_sampling_step = 0
        
    def get_job_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # shouldn't this return job_timestamp?


state = State()

artist_db = modules.artists.ArtistsDatabase(os.path.join(script_path, 'artists.csv'))

styles_filename = cmd_opts.styles_file
prompt_styles = modules.styles.StyleDatabase(styles_filename)

interrogator = modules.interrogate.InterrogateModels("interrogate")

face_restorers = []


def realesrgan_models_names():
    import modules.realesrgan_model
    return [x.name for x in modules.realesrgan_model.get_realesrgan_models(None)]


class OptionInfo:
    def __init__(self, default=None, label="", component=None, component_args=None, onchange=None, show_on_main_page=False):
        self.default = default
        self.label = label
        self.component = component
        self.component_args = component_args
        self.onchange = onchange
        self.section = None
        self.show_on_main_page = show_on_main_page


def options_section(section_identifier, options_dict):
    for k, v in options_dict.items():
        v.section = section_identifier

    return options_dict


hide_dirs = {"visible": not cmd_opts.hide_ui_dir_config}

options_templates = {}

options_templates.update(options_section(('saving-images', "保存图像和网格图/Saving images/grids"), {
    "samples_save": OptionInfo(True, "始终保存所有生成的图像/Always save all generated images"),
    "samples_format": OptionInfo('png', '图像命名方式/File format for images'),
    "samples_filename_pattern": OptionInfo("", "图像命名模式/Images filename pattern"),

    "grid_save": OptionInfo(True, "始终保存所有生成的图像网格/Always save all generated image grids"),
    "grid_format": OptionInfo('png', '网格的文件格式/File format for grids'),
    "grid_extended_filename": OptionInfo(False, "保存网格时将扩展信息（图像生成种子、关键词语句）添加到文件名/Add extended info (seed, prompt) to filename when saving grid"),
    "grid_only_if_multiple": OptionInfo(True, "不保存由一张图像组成的网格/Do not save grids consisting of one picture"),
    "n_rows": OptionInfo(-1, "网格行数:为-1时会进行自动检测,为0时会使其与批量大小相同/Grid row count; use -1 for autodetect and 0 for it to be same as batch size", gr.Slider, {"minimum": -1, "maximum": 16, "step": 1}),

    "enable_pnginfo": OptionInfo(True, "将关于生成参数的文本信息以块的形式保存到png文件中/Save text information about generation parameters as chunks to png files"),
    "save_txt": OptionInfo(False, "在每一个带有生成参数的图像旁,创建一个文本文件/Create a text file next to every image with generation parameters."),
    "save_images_before_face_restoration": OptionInfo(False, "在面部修复前保存一份图像的副本/Save a copy of image before doing face restoration."),
    "jpeg_quality": OptionInfo(80, "保存jpeg图像的质量/Quality for saved jpeg images", gr.Slider, {"minimum": 1, "maximum": 100, "step": 1}),
    "export_for_4chan": OptionInfo(True, "如果PNG大于4MB或任何尺寸大于4000,缩小尺寸并保存为JPG/If PNG image is larger than 4MB or any dimension is larger than 4000, downscale and save copy as JPG"),

    "use_original_name_batch": OptionInfo(False, "在额外标签的批处理过程中,为输出文件名使用原始名称/Use original name for output filename during batch process in extras tab"),
    "save_selected_only": OptionInfo(True, "使用“保存”按钮时,只保存一个选定的图像/When using 'Save' button, only save a single selected image"),
    "do_not_add_watermark": OptionInfo(False, "不在图像中添加水印/Do not add watermark to images"),
}))

options_templates.update(options_section(('saving-paths', "保存路径/Paths for saving"), {
    "outdir_samples": OptionInfo("", "图像的输出目录;如果为空,默认为下面的三个目录/Output directory for images; if empty, defaults to three directories below", component_args=hide_dirs),
    "outdir_txt2img_samples": OptionInfo("outputs/txt2img-images", 'txt2img图像的输出目录/Output directory for txt2img images', component_args=hide_dirs),
    "outdir_img2img_samples": OptionInfo("outputs/img2img-images", 'img2img图像的输出目录/Output directory for img2img images', component_args=hide_dirs),
    "outdir_extras_samples": OptionInfo("outputs/extras-images", '额外标签的输出目录/Output directory for images from extras tab', component_args=hide_dirs),
    "outdir_grids": OptionInfo("", "网格的输出目录;如果为空,默认为下面的两个目录/Output directory for grids; if empty, defaults to two directories below", component_args=hide_dirs),
    "outdir_txt2img_grids": OptionInfo("outputs/txt2img-grids", 'txt2img网格的输出目录/Output directory for txt2img grids', component_args=hide_dirs),
    "outdir_img2img_grids": OptionInfo("outputs/img2img-grids", 'img2img网格的输出目录/Output directory for img2img grids', component_args=hide_dirs),
    "outdir_save": OptionInfo("log/images", "使用“保存”按钮保存图像的目录/Directory for saving images using the Save button", component_args=hide_dirs),
}))

options_templates.update(options_section(('saving-to-dirs', "保存到目录/Saving to a directory"), {
    "save_to_dirs": OptionInfo(False, "将图像保存到子目录/Save images to a subdirectory"),
    "grid_save_to_dirs": OptionInfo(False, "将网格保存到子目录/Save grids to a subdirectory"),
    "use_save_to_dirs_for_ui": OptionInfo(False, "当使用“保存”按钮时,将图像保存到子目录When using \"Save\" button, save images to a subdirectory"),
    "directories_filename_pattern": OptionInfo("", "目录命名方式/Directory name pattern"),
    "directories_max_prompt_words": OptionInfo(8, "最大提示词[prompt_words]模式/Max prompt words for [prompt_words] pattern", gr.Slider, {"minimum": 1, "maximum": 20, "step": 1}),
}))

options_templates.update(options_section(('upscaling', "图像高清化选项/Upscaling"), {
    "ESRGAN_tile": OptionInfo(192, "ESRGAN图像放大器的图块大小,0=不平铺/Tile size for ESRGAN upscalers. 0 = no tiling.", gr.Slider, {"minimum": 0, "maximum": 512, "step": 16}),
    "ESRGAN_tile_overlap": OptionInfo(8, "贴图重叠范围,以ESRGAN图像放大器的像素为单位,低值=可见接缝/Tile overlap, in pixels for ESRGAN upscalers. Low values = visible seam.", gr.Slider, {"minimum": 0, "maximum": 48, "step": 1}),
    "realesrgan_enabled_models": OptionInfo(["Real-ESRGAN x4+", "Real-ESRGAN x4+ Anime 6B"], "选择要在WebUI中显示的RealESRGAN模型(需要重启)/Select which Real-ESRGAN models to show in the web UI. (Requires restart)", gr.CheckboxGroup, lambda: {"choices": realesrgan_models_names()}),
    "SWIN_tile": OptionInfo(192, "无缝拼接图像尺寸来自SwinIR模型/Tile size for all SwinIR.", gr.Slider, {"minimum": 16, "maximum": 512, "step": 16}),
    "SWIN_tile_overlap": OptionInfo(8, "贴图重叠范围,拼接像素来自SwinIR模型,低值=可见接缝/Tile overlap, in pixels for SwinIR. Low values = visible seam.", gr.Slider, {"minimum": 0, "maximum": 48, "step": 1}),
    "ldsr_steps": OptionInfo(100, "LDSR处理步数,低步数=高速度/LDSR processing steps. Lower = faster", gr.Slider, {"minimum": 1, "maximum": 200, "step": 1}),
    "upscaler_for_img2img": OptionInfo(None, "img2img的图像放大器/Upscaler for img2img", gr.Dropdown, lambda: {"choices": [x.name for x in sd_upscalers]}),
}))

options_templates.update(options_section(('face-restoration', "面部修复/Face restoration"), {
    "face_restoration_model": OptionInfo(None, "面部修复模型/Face restoration model", gr.Radio, lambda: {"choices": [x.name() for x in face_restorers]}),
    "code_former_weight": OptionInfo(0.5, "编码器权重:0=效果最大;1=效果最小/CodeFormer weight parameter; 0 = maximum effect; 1 = minimum effect", gr.Slider, {"minimum": 0, "maximum": 1, "step": 0.01}),
    "face_restoration_unload": OptionInfo(False, "处理后将面部修复模型从显存移到内存中/Move face restoration model from VRAM into RAM after processing"),
}))

options_templates.update(options_section(('system', "系统System"), {
    "memmon_poll_rate": OptionInfo(8, "显存在生成过程中每秒询问一次,设置为0表示禁用/VRAM usage polls per second during generation. Set to 0 to disable.", gr.Slider, {"minimum": 0, "maximum": 40, "step": 1}),
    "samples_log_stdout": OptionInfo(False, "总是打印出同一批次信息到标准输出/Always print all generation info to standard output"),
    "multiple_tqdm": OptionInfo(True, "向控制台添加第二个进度条,显示整个作业的进度,不可用于PyCharm控制台/Add a second progress bar to the console that shows progress for an entire job. Broken in PyCharm console."),
}))

options_templates.update(options_section(('sd', "Stable Diffusion"), {
    "sd_model_checkpoint": OptionInfo(None, "Stable Diffusion模型/Stable Diffusion checkpoint", gr.Dropdown, lambda: {"choices": modules.sd_models.checkpoint_tiles()}, show_on_main_page=True),
    "sd_hypernetwork": OptionInfo("None", "Stable Diffusion精细超网络/Stable Diffusion finetune hypernetwork", gr.Dropdown, lambda: {"choices": ["None"] + [x for x in hypernetworks.keys()]}),
    "img2img_color_correction": OptionInfo(False, "对img2img生成的结果应用颜色校正来与原始颜色相匹配/Apply color correction to img2img results to match original colors."),
    "save_images_before_color_correction": OptionInfo(False, "在对img2img生成的结果应用颜色校正之前,保存图像的副本/Save a copy of image before applying color correction to img2img results"),    
    "img2img_fix_steps": OptionInfo(False, "使用img2img,完全执行滑块指定的步数(通常情况下,降噪越少,执行的步数就越少)/With img2img, do exactly the amount of steps the slider specifies (normally you'd do less with less denoising)."),
    "enable_quantization": OptionInfo(False, "在K-diffusion采样器中启动量化来获得更清晰简洁的结果,这可能会改变现有的图像生成种子,需要重新启动才能应用/Enable quantization in K samplers for sharper and cleaner results. This may change existing seeds. Requires restart to apply."),
    "enable_emphasis": OptionInfo(True, "强调:模型更加注重于(文本)内的文本,少量注重于[文本]内的文本/Emphasis: use (text) to make model pay more attention to text and [text] to make it pay less attention"),
    "use_old_emphasis_implementation": OptionInfo(False, "使用旧的强调实现,可以用来繁殖老种子/Use old emphasis implementation. Can be useful to reproduce old seeds."),
    "enable_batch_seeds": OptionInfo(True, "使用K-diffusion采样器批量生成与生成单个图像时相同的图像/Make K-diffusion samplers produce same images in a batch as when making a single image"),
    "filter_nsfw": OptionInfo(False, "过滤NSFW(不适合在公共场合或者上班的时候浏览)内容/Filter NSFW content"),
    'CLIP_ignore_last_layers': OptionInfo(0, "在CLIP模型的最后几层停止/Stop At last layers of CLIP model", gr.Slider, {"minimum": 0, "maximum": 5, "step": 1}),
    "random_artist_categories": OptionInfo([], "当使用随机关键词按钮时,允许选择随机艺术家类别/Allowed categories for random artists selection when using the Roll button", gr.CheckboxGroup, {"choices": artist_db.categories()}),
}))

options_templates.update(options_section(('interrogate', "询问设置/Interrogate Options"), {
    "interrogate_keep_models_in_memory": OptionInfo(False, "询问:将模型保存在显存中/Interrogate: keep models in VRAM"),
    "interrogate_use_builtin_artists": OptionInfo(True, "询问:使用artsts.csv中的艺术家/Interrogate: use artists from artists.csv"),
    "interrogate_clip_num_beams": OptionInfo(1, "询问:集数数量来自BLIP/Interrogate: num_beams for BLIP", gr.Slider, {"minimum": 1, "maximum": 16, "step": 1}),
    "interrogate_clip_min_length": OptionInfo(24, "询问:最小描述长度(不包括艺术家等)/Interrogate: minimum description length (excluding artists, etc..)", gr.Slider, {"minimum": 1, "maximum": 128, "step": 1}),
    "interrogate_clip_max_length": OptionInfo(48, "询问:最大描述长度/Interrogate: maximum description length", gr.Slider, {"minimum": 1, "maximum": 256, "step": 1}),
    "interrogate_clip_dict_limit": OptionInfo(1500, "询问:文本文件中的最大行数(0=无限制)、Interrogate: maximum number of lines in text file (0 = No limit)"),
}))

options_templates.update(options_section(('ui', "用户界面/User interface"), {
    "show_progressbar": OptionInfo(True, "显示进度条/Show progressbar"),
    "show_progress_every_n_steps": OptionInfo(0, "每N个采样步数显示图像的创建进度,设置0禁用/Show show image creation progress every N sampling steps. Set 0 to disable.", gr.Slider, {"minimum": 0, "maximum": 32, "step": 1}),
    "return_grid": OptionInfo(True, "在web中显示网格/Show grid in results for web"),
       "do_not_show_images": OptionInfo(False, "网页不显示任何生成图像的结果/Do not show any images in results for web"),
    "add_model_hash_to_info": OptionInfo(True, "在生成信息中添加模型哈希/Add model hash to generation information"),
    "add_model_name_to_info": OptionInfo(False, "将模型名称添加到生成信息中/Add model name to generation information"),
    "font": OptionInfo("", "具有文本的图像网格的字体/Font for image grids that have text"),
    "js_modal_lightbox": OptionInfo(True, "启用整页图像查看界面/Enable full page image viewer"),
    "js_modal_lightbox_initialy_zoomed": OptionInfo(True, "在整页图像查看界面中默认显示放大的图像/Show images zoomed in by default in full page image viewer"),
    "show_progress_in_title": OptionInfo(True, "在浏览器标题中显示生成进度/Show generation progress in window title."),
}))

options_templates.update(options_section(('sampler-params', "采样工具参数/Sampler parameters"), {
        "hide_samplers": OptionInfo([], "在用户界面中隐藏采样工具(需要重新启动)/Hide samplers in user interface (requires restart)", gr.CheckboxGroup, lambda: {"choices": [x.name for x in sd_samplers.all_samplers]}),
  "eta_ddim": OptionInfo(0.0, "eta(噪声倍增器)用于DDIM/eta (noise multiplier) for DDIM", gr.Slider, {"minimum": 0.0, "maximum": 1.0, "step": 0.01}),
   "eta_ancestral": OptionInfo(1.0, "eta(噪声倍增器)用于原始采样工具/eta (noise multiplier) for ancestral samplers", gr.Slider, {"minimum": 0.0, "maximum": 1.0, "step": 0.01}),
  "ddim_discretize": OptionInfo('uniform', "img2img DDIM 离散化/img2img DDIM discretize", gr.Radio, {"choices": ['uniform', 'quad']}),
  's_churn': OptionInfo(0.0, "sigma混合/sigma churn", gr.Slider, {"minimum": 0.0, "maximum": 1.0, "step": 0.01}),
  's_tmin':  OptionInfo(0.0, "sigma时长/sigma tmin",  gr.Slider, {"minimum": 0.0, "maximum": 1.0, "step": 0.01}),
  's_noise': OptionInfo(1.0, "sigma噪点/sigma noise", gr.Slider, {"minimum": 0.0, "maximum": 1.0, "step": 0.01}),
  'eta_noise_seed_delta': OptionInfo(0, "delta噪声种子/Eta noise seed delta", gr.Number, {"precision": 0}),
}))

options_templates.update(options_section(('statement', "Stable Diffusion webui版个人汉化说明-10111300"), {
    "statement1": OptionInfo('本汉化仅供学习交流使用'),
    "statement2": OptionInfo('webui如有新界面,我会尽快更新'),
    "statement3": OptionInfo('因为本人不是深度学习从业人员,汉化上不保证准确性'),
    "statement4": OptionInfo('欢迎给出更好的翻译建议'),
    "statement5": OptionInfo('交流群:764844927'),
}))

class Options:
    data = None
    data_labels = options_templates
    typemap = {int: float}

    def __init__(self):
        self.data = {k: v.default for k, v in self.data_labels.items()}

    def __setattr__(self, key, value):
        if self.data is not None:
            if key in self.data:
                self.data[key] = value

        return super(Options, self).__setattr__(key, value)

    def __getattr__(self, item):
        if self.data is not None:
            if item in self.data:
                return self.data[item]

        if item in self.data_labels:
            return self.data_labels[item].default

        return super(Options, self).__getattribute__(item)

    def save(self, filename):
        with open(filename, "w", encoding="utf8") as file:
            json.dump(self.data, file)

    def same_type(self, x, y):
        if x is None or y is None:
            return True

        type_x = self.typemap.get(type(x), type(x))
        type_y = self.typemap.get(type(y), type(y))

        return type_x == type_y

    def load(self, filename):
        with open(filename, "r", encoding="utf8") as file:
            self.data = json.load(file)

        bad_settings = 0
        for k, v in self.data.items():
            info = self.data_labels.get(k, None)
            if info is not None and not self.same_type(info.default, v):
                print(f"Warning: bad setting value: {k}: {v} ({type(v).__name__}; expected {type(info.default).__name__})", file=sys.stderr)
                bad_settings += 1

        if bad_settings > 0:
            print(f"The program is likely to not work with bad settings.\nSettings file: {filename}\nEither fix the file, or delete it and restart.", file=sys.stderr)

    def onchange(self, key, func):
        item = self.data_labels.get(key)
        item.onchange = func

    def dumpjson(self):
        d = {k: self.data.get(k, self.data_labels.get(k).default) for k in self.data_labels.keys()}
        return json.dumps(d)


opts = Options()
if os.path.exists(config_filename):
    opts.load(config_filename)

sd_upscalers = []

sd_model = None

progress_print_out = sys.stdout


class TotalTQDM:
    def __init__(self):
        self._tqdm = None

    def reset(self):
        self._tqdm = tqdm.tqdm(
            desc="Total progress",
            total=state.job_count * state.sampling_steps,
            position=1,
            file=progress_print_out
        )

    def update(self):
        if not opts.multiple_tqdm or cmd_opts.disable_console_progressbars:
            return
        if self._tqdm is None:
            self.reset()
        self._tqdm.update()

    def updateTotal(self, new_total):
        if not opts.multiple_tqdm or cmd_opts.disable_console_progressbars:
            return
        if self._tqdm is None:
            self.reset()
        self._tqdm.total=new_total

    def clear(self):
        if self._tqdm is not None:
            self._tqdm.close()
            self._tqdm = None


total_tqdm = TotalTQDM()

mem_mon = modules.memmon.MemUsageMonitor("MemMon", device, opts)
mem_mon.start()
