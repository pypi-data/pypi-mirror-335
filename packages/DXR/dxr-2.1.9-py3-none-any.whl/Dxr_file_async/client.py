import asyncio
import time
import grpc
from grpc import aio
import zipfile
from . import zip_service_pb2
from . import zip_service_pb2_grpc
import logging     
import os
import threading

class ZipClient:
    def __init__(self, ip, zip_progress_callback, download_progress_callback, download_completion_callback=None):
        self.stub = None
        self.zip_progress_callback = zip_progress_callback
        self.download_progress_callback = download_progress_callback
        self.download_completion_callback = download_completion_callback
        self.ip = ip
        self.task = None  # this is to keep track of the task
        self.thread = None  # this is to keep track of the separate thread
        

    async def start(self, directory):
        # Create gRPC channel and stub
        options = [
            ('grpc.enable_retries', 1),
            ('grpc.keepalive_time_ms', 60000),     # send keepalive every 10 seconds
            ('grpc.keepalive_timeout_ms', 60000),  # Timeout if keepalive ping not responded to
        ]
        channel = aio.insecure_channel(f'{self.ip}:50051', options=options)
        self.stub = zip_service_pb2_grpc.ZipServiceStub(channel)
        # response = self.stub.SomeOperation(request, timeout=600)

        try:
            # Call StartZip
            request = zip_service_pb2.ZipRequest(dir=directory)
            async for response in self.stub.StartZip(request):
                self.zip_progress_callback(response.progress)

            # 获取用户目录
            user_dir = os.path.expanduser('~')
            # 要创建/检查的目录
            dxr_dir = os.path.join(user_dir, 'dxr')

            # 检查目录是否存在，如果不存在则创建
            if not os.path.exists(dxr_dir):
                os.makedirs(dxr_dir)

            # 你要写入的文件的最终路径
            file_path = os.path.join(dxr_dir, 'downloaded.zip')

            # 打开文件并准备写入数据
            with open(file_path, 'wb') as f:
                # Call DownloadZip
                request = zip_service_pb2.DownloadRequest(filename='output.zip')
                
                async for response in self.stub.DownloadZip(request):
                    if response.data:
                        # 将接收到的数据直接写入文件
                        f.write(response.data)
                        progress = response.sent_size / response.total_size
                        self.download_progress_callback(progress)
        except:
            print('Download task cancelled.')
            if self.download_completion_callback:
                self.download_completion_callback(-1)
        else:
            print('Download task completed.')
            if self.download_completion_callback:
                self.download_completion_callback(0)
        finally:
            await channel.close()
        
        
    def start_sync(self, directory):
        if self.thread is not None and self.thread.is_alive():
            print("Thread already running. Please wait for current operation to finish or stop.")
            return
        print("Starting download task.", directory)
        self.thread = threading.Thread(target = self._start_thread, args = (directory,))
        self.thread.start()
        
    def _start_thread(self, directory):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.task = loop.create_task(self.start(directory))  # creates a new task
            loop.run_until_complete(self.task)  # runs the task
        except Exception as e:
            raise e
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    def stop_sync(self):
        if self.task:   # if a task exists, stop it
            try:
                self.task.cancel()
                print('Stopping download task.')
            except:
                print("Download task stop failed.")
        

def zip_progress_update(progress):
    print('Zip Progress: {:.2f}'.format(progress * 100))

def download_progress_update(progress):
    print('Download Progress: {:.2f}'.format(progress * 100))


# User code:
if __name__ == '__main__':
    logging.basicConfig()
    client = ZipClient(zip_progress_update, download_progress_update, ip="10.10.0.195")
    client.start_sync('/Users/luzhipeng/Desktop/Images/图片')
    
    time.sleep(10)
    
    client.stop_sync()
