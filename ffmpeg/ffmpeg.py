import json
import os
import platform
import zipfile
import tarfile
import subprocess


class FFmpeg:
    __threads = 1
    __input_file = []
    __output_path = None
    __output_name = None
    __subtitle_file = []
    __crf = 22
    __preset = 'medium'
    __x265 = False
    __x264 = False
    __videos = []
    __audios = []
    __subtitles = []
    __scale = None
    __tune = 'film'
    ffmpeg_file = ''
    ffprobe_file = ''
    __run = []
    __gpu = False

    def __init__(self, input_file, output_path, output_name):
        self.__input_file = input_file
        self.__output_path = output_path
        self.__output_name = output_name
        self.__subtitle_file = []
        self.__videos = []
        self.__audios = []
        self.__subtitles = []

    @staticmethod
    def __ffmpeg_check():
        if os.path.exists('ffmpeg_runner'):
            if FFmpeg.ffmpeg_file == '':
                os_name = platform.system()
                if os_name == 'Windows':
                    FFmpeg.ffmpeg_file = './ffmpeg_runner/ffmpeg-5.0.1-essentials_build/bin/ffmpeg'
                    FFmpeg.ffprobe_file = './ffmpeg_runner/ffmpeg-5.0.1-essentials_build/bin/ffprobe'
                elif os_name == 'Linux':
                    FFmpeg.ffmpeg_file = './ffmpeg_runner/ffmpeg-5.0.1-amd64-static/ffmpeg'
                    FFmpeg.ffprobe_file = './ffmpeg_runner/ffmpeg-5.0.1-amd64-static/ffprobe'
            return True

        return False

    @staticmethod
    def __ffmpeg_donwload():
        os_name = platform.system()
        print(f'OS: {os_name}')
        if os_name == 'Windows':
            print('Downloading ffmpeg...')
            if not os.path.exists('ffmpeg-5.0.1-essentials_build.zip'):
                os.system(
                    'curl https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-5.0.1-essentials_build.zip -O ffmpeg-5.0.1-essentials_build.zip')
            with zipfile.ZipFile('ffmpeg-5.0.1-essentials_build.zip', 'r') as zip_ref:
                zip_ref.extractall('ffmpeg_runner')
            os.remove('ffmpeg-5.0.1-essentials_build.zip')
            FFmpeg.ffmpeg_file = './ffmpeg_runner/ffmpeg-5.0.1-essentials_build/bin/ffmpeg'
            FFmpeg.ffprobe_file = './ffmpeg_runner/ffmpeg-5.0.1-essentials_build/bin/ffprobe'
            print('Download complete.')
        elif os_name == 'Linux':
            print('Downloading ffmpeg...')
            if not os.path.exists('ffmpeg-5.0.1-essentials_build.zip'):
                os.system(
                    'curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -O ffmpeg-release-amd64-static.tar.xz')
            with tarfile.open('ffmpeg-release-amd64-static.tar.xz') as tar_ref:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar_ref, "ffmpeg_runner")
            os.remove('ffmpeg-release-amd64-static.tar.xz')
            FFmpeg.ffmpeg_file = './ffmpeg_runner/ffmpeg-5.0.1-amd64-static/ffmpeg'
            FFmpeg.ffprobe_file = './ffmpeg_runner/ffmpeg-5.0.1-amd64-static/ffprobe'
            print('Download complete.')

    @staticmethod
    def ffmpeg_exists():
        if not FFmpeg.__ffmpeg_check():
            FFmpeg.__ffmpeg_donwload()

    def set_threads(self, count):
        self.__threads = count

    def get_threads(self):
        return self.__threads

    def add_subtitle(self, file):
        self.__subtitle_file.append(file)

    def get_subtitle(self):
        return self.__subtitle_file

    def set_crf(self, crf):
        self.__crf = crf

    def get_crf(self):
        return self.__crf

    def set_preset(self, preset):
        if preset not in ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo']:
            print('Invalid preset')
            return

        self.__preset = preset

    def get_preset(self):
        return self.__preset

    def set_scale(self, scale):
        if scale not in ['360', '480', '720', '1080']:
            print('Invalid scale')
            return

        scale_map = {
            '360': 640,
            '480': 854,
            '720': 1280,
            '1080': 1920
        }
        self.__scale = scale_map[scale]

    def set_tune(self, tune):
        if tune not in ['film', 'animation', 'grain', 'stillimage', 'fastdecode', 'zerolatency', 'psnr', 'ssim']:
            print('Invalid tune')
            return

        self.__tune = tune

    def get_tune(self):
        return self.__tune

    def select_videos(self, indexes):
        self.__videos = indexes

    def select_audios(self, indexes):
        self.__audios = indexes

    def select_subtitles(self, indexes):
        self.__subtitles = indexes

    def x265(self, activate: bool):
        self.__x265 = activate

    def x264(self, activate: bool):
        self.__x264 = activate

    def gpu(self, activate: bool):
        self.__gpu = activate

    def get_source_subtitles(self):
        map = subprocess.Popen([self.ffprobe_file, '-select_streams', 's', '-show_entries', 'stream=index:stream_tags',
                               '-of', 'json', self.__input_file[0]], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return json.loads(map.stdout.read())['streams']

    def get_source_audios(self):
        map = subprocess.Popen([self.ffprobe_file, '-select_streams', 'a', '-show_entries', 'stream=index:stream_tags',
                               '-of', 'json', self.__input_file[0]], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return json.loads(map.stdout.read())['streams']

    def get_source_videos(self):
        print('Videos:')
        map = subprocess.Popen([self.ffprobe_file, '-select_streams', 'v', '-show_entries', 'stream=index:stream_tags',
                               '-of', 'json', self.__input_file[0]], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return json.loads(map.stdout.read())['streams']

    def encoding(self):
        if not self.__ffmpeg_check():
            self.__ffmpeg_donwload()

        if not os.path.exists(self.__output_path):
            os.mkdir(self.__output_path)

        run = [
            self.ffmpeg_file,
            '-y',
            '-hwaccel',
            'auto',
            '-i',
            f'"{self.__input_file[0]}"',
            '-crf',
            f'{self.__crf}',
            '-preset',
            f'{self.__preset}',
            '-tune',
            f'{self.__tune}',
            '-c:a',
            'aac',
            '-b:a',
            '128k'
        ]

        if self.__x265:
            run.extend(['-c:v', 'libx265'])

        if self.__x264:
            run.extend(['-c:v', 'libx264'])
            if self.__gpu:
                run.extend(['-x264opts', 'opencl'])

        if len(self.__subtitle_file) > 0 and self.__scale is None:
            run.append('-vf')
            ass = ''

            for subtitle in self.__subtitle_file:
                ass += f'ass={subtitle},'

            ass = ass[:-1]

            run.append(f"'{ass}'")

        if self.__scale is not None and len(self.__subtitle_file) == 0:
            run.extend(['-vf', f'"scale={self.__scale}:trunc(ow/a/2)*2"'])

        if self.__scale is not None and len(self.__subtitle_file) > 0:
            ass = ''

            for subtitle in self.__subtitle_file:
                ass += f'ass={subtitle},'

            ass = ass[:-1]

            run.extend(
                ['-vf', f"'scale={self.__scale}:trunc(ow/a/2)*2,{ass}'"])
        if len(self.__videos) > 0:
            for i in range(0, len(self.__videos)):
                run.extend(['-map', f'0:{self.__videos[i]}'])

        if len(self.__audios) > 0:
            for i in range(0, len(self.__audios)):
                run.extend(['-map', f'0:{self.__audios[i]}'])

        if len(self.__subtitles) > 0:
            for i in range(0, len(self.__audios)):
                run.extend(['-map', f'0:{self.__audios[i]}'])

        run.extend(['-threads', f'{self.__threads}'])
        run.extend(['-progress', '-', '-nostats'])

        run.append(f'"{self.__output_path}/{self.__output_name}"')

        self.run = run

    def concat(self):
        if not self.__ffmpeg_check():
            self.__ffmpeg_donwload()

        if not os.path.exists(self.__output_path):
            os.mkdir(self.__output_path)

        file = open(f"./inputs.txt", "w")
        file.write(f"file {self.__input_file[0]}\nfile {self.__input_file[1]}")
        file.close()

        run = [
            self.ffmpeg_file,
            '-y',
            '-f',
            'concat',
            '-i',
            f'./inputs.txt',
            '-segment_time_metadata',
            '1',
            '-vf',
            'select=concatdec_select',
            '-af',
            'aselect=concatdec_select,aresample=async=1',
            '-progress', '-', '-nostats',
            f'"{self.__output_path}/{self.__output_name}"'
        ]

        self.run = run

    def exec(self, in_notebook=False):
        if not in_notebook:
            subprocess.run(self.run)
        else:
            import IPython
            IPython.get_ipython().run_cell(f"""!{' '.join(self.run)}""")
