import cv2
import subprocess as sp

class VideoStreamer:
    """
    VideoStreamer类用于创建和管理用于视频流传输的FFmpeg子进程。

    属性：
    srs_rtmp_url: RTMP URL，用于推送流到RTMP服务器。
    width: 视频宽度。
    height: 视频高度。
    command: FFmpeg子进程的命令行参数。
    pipe: FFmpeg子进程。

    方法：
    push_frame: 推送视频帧到RTMP服务器。
    close: 终止FFmpeg子进程。
    """
    
    def __init__(self, alias, ip="127.0.0.1", fps=30, width=1920, height=1080):
        # 将ip和别名拼接成RTMP URL
        self.srs_rtmp_url = f"rtmp://{ip}/live/{alias}"
        self.width = width
        self.height = height
        # 设置ffmpeg命令
        self.command = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '{}x{}'.format(self.width, self.height),
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'superfast',
            '-tune', 'zerolatency',
            '-f', 'flv',
            self.srs_rtmp_url
        ]
        # 启动ffmpeg进程
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)

    def push_frame(self, frame):
        # 将帧推送到RTMP服务器
        self.pipe.stdin.write(frame.tobytes())

    def close(self):
        # 终止ffmpeg进程
        self.pipe.terminate()

if __name__ == "__main__":
    # 设置别名和视频流URL
    alias = "stream"
    pull_stream_url = 0

    # 打开视频流
    cap = cv2.VideoCapture(pull_stream_url)
    # 获取视频的宽度和高度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 创建VideoStreamer对象
    streamer = VideoStreamer(alias, width=width, height=height)
    try:
        # 循环读取视频帧，并推送到RTMP服务器
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            streamer.push_frame(frame)
    finally:
        # 释放资源
        cap.release()
        streamer.close()
