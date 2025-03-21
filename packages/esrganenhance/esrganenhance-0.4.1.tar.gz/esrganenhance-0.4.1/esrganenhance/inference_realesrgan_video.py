import argparse
import math

import cv2
import mimetypes
import numpy as np
import os
import shutil
import subprocess
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from os import path as osp
from tqdm import tqdm
from decimal import Decimal

from realesrgan.utils import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

try:
    import ffmpeg
except ImportError:
    import pip

    pip.main(['install', '--user', 'ffmpeg-python'])
    import ffmpeg

def get_video_meta_info(video_path):
    try:
        ret = {}
        probe = ffmpeg.probe(video_path)
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
        ret['width'] = video_streams[0]['width']
        ret['height'] = video_streams[0]['height']
        ret['fps'] = eval(video_streams[0]['avg_frame_rate'])
        ret['audio'] = ffmpeg.input(video_path).audio if has_audio else None
        ret['nb_frames'] = int(video_streams[0]['nb_frames'])
        ret['duration'] = ret['nb_frames'] / ret['fps']
        # 获取视频文件大小（字节）
        file_size = os.path.getsize(video_path)
        # 将文件大小转换为 MB 格式
        size_in_mb = file_size / (1024 * 1024)
        ret['size'] = size_in_mb
    except Exception as e:
        os.remove(video_path)
        raise Exception(f'{video_path} get_video_meta_info error: {e}')
    return ret

def get_alloc_time(duration, num_process, idx):
    """
    计算第 idx 个片段的开始时间和时长
    """
    if isinstance(duration, float):
        duration = Decimal(str(duration))  # 将浮点数转换为 Decimal 对象
    if duration > num_process:
        num_base = int(duration) // num_process
        num_extra = int(duration) % num_process
        # start_time 片段开始时间
        start_time = idx * num_base + min(idx, num_extra)
        # part_time 该片段的时长，如果该段是最后一段，则将剩余的时间分配给它
        part_time = (num_base + (1 if idx < num_extra else 0)) if idx != num_process - 1 else (
                duration - start_time)
        return start_time, part_time
    return idx, 1 if idx != num_process - 1 else (duration - idx)


def get_sub_video(args, num_process, process_idx):
    duration = get_video_meta_info(args.input)['duration']
    if num_process == 1:
        return args.input, duration
    start_time, part_time = get_alloc_time(duration, num_process, process_idx)
    os.makedirs(osp.join(args.output, f'{args.video_name}_inp_tmp_videos'), exist_ok=True)
    out_path = osp.join(args.output, f'{args.video_name}_inp_tmp_videos', f'{process_idx:03d}.mp4')
    cmd = [
        args.ffmpeg_bin, f'-i {args.input}', '-ss', f'{start_time}',
        f'-t {part_time}', '-async 1', out_path, '-y'
    ]
    subprocess.call(' '.join(cmd), shell=True)
    return out_path, part_time


class Reader:

    def __init__(self, args, total_workers=1, worker_idx=0):
        self.args = args
        input_type = mimetypes.guess_type(args.input)[0]
        self.input_type = 'folder' if input_type is None else input_type
        self.paths = []  # for image&folder type
        self.audio = None
        self.input_fps = None
        video_path, part_time = get_sub_video(args, total_workers, worker_idx)
        self.stream_reader = (
            ffmpeg.input(video_path).output('pipe:', format='rawvideo', pix_fmt='bgr24',
                                            loglevel='error').run_async(
                pipe_stdin=True, pipe_stdout=True, cmd=args.ffmpeg_bin))
        meta = get_video_meta_info(video_path)
        self.width = meta['width']
        self.height = meta['height']
        self.input_fps = meta['fps']
        self.audio = meta['audio']
        self.nb_frames = meta['nb_frames']
        self.idx = 0

    def get_resolution(self):
        return self.height, self.width

    def get_fps(self):
        if self.args.fps is not None:
            return self.args.fps
        elif self.input_fps is not None:
            return self.input_fps
        return 24

    def get_audio(self):
        return self.audio

    def __len__(self):
        return self.nb_frames

    def get_frame_from_stream(self):
        img_bytes = self.stream_reader.stdout.read(self.width * self.height * 3)  # 3 bytes for one pixel
        if not img_bytes:
            return None
        img = np.frombuffer(img_bytes, np.uint8).reshape([self.height, self.width, 3])
        return img

    def get_frame_from_list(self):
        if self.idx >= self.nb_frames:
            return None
        img = cv2.imread(self.paths[self.idx])
        self.idx += 1
        return img

    def get_frame(self):
        if self.input_type.startswith('video'):
            return self.get_frame_from_stream()
        else:
            return self.get_frame_from_list()

    def close(self):
        if self.input_type.startswith('video'):
            self.stream_reader.stdin.close()
            self.stream_reader.wait()


class Writer:

    def __init__(self, args, audio, height, width, video_save_path, fps):
        out_width, out_height = int(args.outscale * width), int(args.outscale * height)
        if out_height > 2160:
            print('You are generating video that is larger than 4K, which will be very slow due to IO speed.',
                  'We highly recommend to decrease the outscale(aka, -s).')

        if audio is not None:
            self.stream_writer = (
                ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{out_width}x{out_height}',
                             framerate=fps).output(
                    audio,
                    video_save_path,
                    pix_fmt='yuv420p',
                    vcodec='libx264',
                    loglevel='error',
                    acodec='copy').overwrite_output().run_async(
                    pipe_stdin=True, pipe_stdout=True, cmd=args.ffmpeg_bin))
        else:
            self.stream_writer = (
                ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{out_width}x{out_height}',
                             framerate=fps).output(
                    video_save_path, pix_fmt='yuv420p', vcodec='libx264',
                    loglevel='error').overwrite_output().run_async(
                    pipe_stdin=True, pipe_stdout=True, cmd=args.ffmpeg_bin))

    def write_frame(self, frame):
        frame = frame.astype(np.uint8).tobytes()
        self.stream_writer.stdin.write(frame)

    def close(self):
        self.stream_writer.stdin.close()
        self.stream_writer.wait()


def inference_video(args, video_save_path, device=None, total_workers=1, worker_idx=0):
    # ---------------------- determine models according to model names ---------------------- #
    args.model_name = args.model_name.split('.pth')[0]
    if args.model_name == 'RealESRGAN_x4plus':  # x4 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth']
    elif args.model_name == 'RealESRNet_x4plus':  # x4 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth']
    elif args.model_name == 'RealESRGAN_x4plus_anime_6B':  # x4 RRDBNet model with 6 blocks
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
        file_url = [
            'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth']
    elif args.model_name == 'RealESRGAN_x2plus':  # x2 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        netscale = 2
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth']
    elif args.model_name == 'realesr-animevideov3':  # x4 VGG-style model (XS size)
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu')
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth']
    elif args.model_name == 'realesr-general-x4v3':  # x4 VGG-style model (S size)
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu')
        netscale = 4
        file_url = [
            'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth',
            'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth'
        ]
    else:
        raise ValueError('Unknown model name')
    # ---------------------- determine model paths ---------------------- #
    model_path = os.path.join('../weights', args.model_name + '.pth')
    if not os.path.isfile(model_path):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        for url in file_url:
            # model_path will be updated
            model_path = load_file_from_url(
                url=url, model_dir=os.path.join(ROOT_DIR, 'weights'), progress=True)

    # use dni to control the denoise strength
    dni_weight = None
    if args.model_name == 'realesr-general-x4v3' and args.denoise_strength != 1:
        wdn_model_path = model_path.replace('realesr-general-x4v3', 'realesr-general-wdn-x4v3')
        model_path = [model_path, wdn_model_path]
        dni_weight = [args.denoise_strength, 1 - args.denoise_strength]

    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        dni_weight=dni_weight,
        model=model,
        tile=args.tile,
        tile_pad=args.tile_pad,
        pre_pad=args.pre_pad,
        half=not args.fp32,
        device=device,
    )
    if 'anime' in args.model_name and args.face_enhance:
        print('face_enhance is not supported in anime models, we turned this option off for you. '
              'if you insist on turning it on, please manually comment the relevant lines of code.')
        args.face_enhance = False

    if args.face_enhance:  # Use GFPGAN for face enhancement
        from gfpgan import GFPGANer
        face_enhancer = GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
            upscale=args.outscale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=upsampler)  # TODO support custom device
    else:
        face_enhancer = None
    reader = Reader(args, total_workers, worker_idx)
    audio = reader.get_audio()
    height, width = reader.get_resolution()
    fps = reader.get_fps()
    writer = Writer(args, audio, height, width, video_save_path, fps)
    pbar = tqdm(total=len(reader), unit='frame', desc='inference')

    while True:
        img = reader.get_frame()
        if img is None:
            break
        try:
            if args.face_enhance:
                _, _, output = face_enhancer.enhance(img, has_aligned=False, only_center_face=False,
                                                     paste_back=True)
            else:
                output, _ = upsampler.enhance(img, outscale=args.outscale)
        except RuntimeError as error:
            print('Error', error)
            print('If you encounter CUDA out of memory, try to set --tile with a smaller number.')
            raise Exception(f'Error,{error}')
        else:
            writer.write_frame(output)
        torch.cuda.synchronize(device)
        pbar.update(1)

    reader.close()
    writer.close()


class ESRGANer:
    def __init__(self, logger, **kwargs):
        self.logger = logger
        self.args = kwargs

    def infer_video(self, args):
        args.video_name = osp.splitext(os.path.basename(args.input))[0]
        video_save_path = args.video_save_path
        num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
        num_process = min(num_gpus, math.ceil(get_video_meta_info(args.input)['duration']))
        self.logger.info(f'num_process:{num_process},num_gpus:{num_gpus}')
        # 如果只有一个 GPU 或者只有 CPU 可用，则不必进行调度
        if num_process == 1 or not torch.cuda.is_available():
            try:
                inference_video(args, video_save_path)
            except Exception as e:
                self.logger.error(f'inference_video error : {e}')
                raise Exception(f'inference_video error : {e}')
        ctx = torch.multiprocessing.get_context('spawn')
        pool = ctx.Pool(num_process)
        os.makedirs(osp.join(args.output, f'{args.video_name}_out_tmp_videos'), exist_ok=True)
        pbar = tqdm(total=num_process, unit='sub_video', desc='inference')
        for i in range(num_process):
            sub_video_save_path = osp.join(args.output, f'{args.video_name}_out_tmp_videos', f'{i:03d}.mp4')
            # 如果 num_process == num_gpus，即视频时长大于GPU数量，则每个进程使用一个 GPU，
            # 否则使用 hash(str(i))%num_gpus 随机分配GPU
            gpu_idx = i % num_gpus if num_process == num_gpus else hash(str(i)) % num_gpus
            pool.apply_async(
                inference_video,
                args=(args, sub_video_save_path, torch.device(gpu_idx), num_process, i),
                callback=lambda arg: pbar.update(1))
        pool.close()
        pool.join()
        # combine sub videos
        # prepare vidlist.txt
        with open(f'{args.output}/{args.video_name}_vidlist.txt', 'w') as f:
            for i in range(num_process):
                f.write(f'file \'{args.video_name}_out_tmp_videos/{i:03d}.mp4\'\n')

        cmd = [
            args.ffmpeg_bin, '-f', 'concat', '-safe', '0', '-i', f'{args.output}/{args.video_name}_vidlist.txt', '-c',
            'copy', f'{video_save_path}', '-y'
        ]
        self.logger.info(f'cmd: {" ".join(cmd)}')
        subprocess.call(cmd)
        shutil.rmtree(osp.join(args.output, f'{args.video_name}_out_tmp_videos'))
        if osp.exists(osp.join(args.output, f'{args.video_name}_inp_tmp_videos')):
            shutil.rmtree(osp.join(args.output, f'{args.video_name}_inp_tmp_videos'))
        os.remove(f'{args.output}/{args.video_name}_vidlist.txt')

    def run(self, input_path, output_path):
        """Inference demo for Real-ESRGAN.
        It mainly for restoring anime videos.

        """
        parser = argparse.ArgumentParser()
        # 从 self.args 中获取默认值，如果不存在则使用默认值
        parser.add_argument('-i', '--input', type=str, default=input_path,
                            help='Input video, image or folder')
        parser.add_argument('-save', '--video_save_path', type=str,
                            default=output_path,
                            help='video_save_path')
        parser.add_argument(
            '-n',
            '--model_name',
            type=str,
            default=self.args.get('model_name', 'realesr-animevideov3'),
            help=(
                'Model names: realesr-animevideov3 | RealESRGAN_x4plus_anime_6B | RealESRGAN_x4plus | RealESRNet_x4plus |'
                ' RealESRGAN_x2plus | realesr-general-x4v3'
                'Default:realesr-'))
        parser.add_argument('-o', '--output', type=str,
                            default=os.path.join(os.path.dirname(os.path.abspath(input_path)), 'tmp'),
                            help='Output folder')
        parser.add_argument(
            '-dn',
            '--denoise_strength',
            type=float,
            default=self.args.get('denoise_strength', 0.5),
            help=('Denoise strength. 0 for weak denoise (keep noise), 1 for strong denoise ability. '
                  'Only used for the realesr-general-x4v3 model'))
        parser.add_argument('-s', '--outscale', type=float, default=self.args.get('outscale', 4),
                            help='The final upsampling scale of the image')
        parser.add_argument('--suffix', type=str, default=self.args.get('suffix', 'out'),
                            help='Suffix of the restored video')
        parser.add_argument('-t', '--tile', type=int, default=self.args.get('tile', 0),
                            help='Tile size, 0 for no tile during testing')
        parser.add_argument('--tile_pad', type=int, default=self.args.get('tile_pad', 10), help='Tile padding')
        parser.add_argument('--pre_pad', type=int, default=self.args.get('pre_pad', 0),
                            help='Pre padding size at each border')
        parser.add_argument('--face_enhance', action='store_true', default=self.args.get('face_enhance', False),
                            help='Use GFPGAN to enhance face')
        parser.add_argument(
            '--fp32', action='store_true', default=self.args.get('fp32', False),
            help='Use fp32 precision during inference. Default: fp16 (half precision).')
        parser.add_argument('--fps', type=float, default=self.args.get('fps', None), help='FPS of the output video')
        parser.add_argument('--ffmpeg_bin', type=str, default=self.args.get('ffmpeg_bin', 'ffmpeg'),
                            help='The path to ffmpeg')
        parser.add_argument('--extract_frame_first', action='store_true',
                            default=self.args.get('extract_frame_first', False))
        parser.add_argument('--num_process_per_gpu', type=int, default=self.args.get('num_process_per_gpu', 1))

        parser.add_argument(
            '--alpha_upsampler',
            type=str,
            default=self.args.get('alpha_upsampler', '../realesrgan'),
            help='The upsampler for the alpha channels. Options: realesrgan | bicubic')
        parser.add_argument(
            '--ext',
            type=str,
            default=self.args.get('ext', 'auto'),
            help='Image extension. Options: auto | jpg | png, auto means using the same extension as inputs')
        args = parser.parse_args()
        os.makedirs(args.output, exist_ok=True)
        try:
            self.infer_video(args)
        except Exception as e:
            raise e


def NewESRGANer(logger, **args):
    return ESRGANer(logger, **args)


if __name__ == '__main__':
    duration = 323.12
    num_gpus = 25
    num_process = min(num_gpus, math.ceil(duration))
    for i in range(num_process):
        start_time, part_time = get_alloc_time(duration, num_process, i)
        gpu_idx = i % num_gpus if num_process == num_gpus else hash(str(i)) % num_gpus
        print(f'gpu_idx:{gpu_idx},start_time:{start_time},part_time:{part_time}')
