import os
import zipfile
import asyncio
import grpc
import pathlib
from grpc import aio
from . import zip_service_pb2
from . import zip_service_pb2_grpc
import logging


class ZipService(zip_service_pb2_grpc.ZipServiceServicer):

    async def StartZip(self, request, context):
        speed, directory_to_zip = request.dir.split('|')
        self.speed = int(speed)
        print(f"Start zip directory: {directory_to_zip}")
        total_size = sum(f.stat().st_size for f in pathlib.Path(directory_to_zip).rglob('*') if f.is_file())
        zipped_size = 0
        loop = asyncio.get_event_loop()

        with zipfile.ZipFile('output.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
            print(f"Total size: {total_size}")
            for dirpath, dirnames, filenames in os.walk(directory_to_zip):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    file_size = os.path.getsize(file_path)
                    await loop.run_in_executor(None, zf.write, file_path)
                    zipped_size += file_size
                    progress = zipped_size / total_size
                    yield zip_service_pb2.ZipProgress(progress=progress)

    async def DownloadZip(self, request, context):
        chunk_size = 1024 * 100  # 1MB
        total_sent_size = 0

        with open('output.zip', 'rb') as f:
            file_size = os.path.getsize('output.zip')
            while True:
                read_data = f.read(chunk_size)
                total_sent_size += len(read_data)

                if len(read_data) == 0:
                    return
                
                if self.speed > 0:
                    print(f"Sleeping for {len(read_data) / self.speed} seconds")
                    await asyncio.sleep(len(read_data) / self.speed)
                
                yield zip_service_pb2.ZipChunk(data=read_data, total_size=file_size, sent_size=total_sent_size)

    @classmethod
    async def serve(cls):
        server = aio.server()
        zip_service_pb2_grpc.add_ZipServiceServicer_to_server(cls(), server)
        server.add_insecure_port('[::]:50051')
        print("Starting server. Listening on port 50051.")
        await server.start()
        await server.wait_for_termination()

    @classmethod
    def start_sync(cls):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(cls.serve())
        finally:
            loop.close()
            asyncio.set_event_loop(None)


if __name__ == "__main__":
    logging.basicConfig()
    ZipService.start_sync()
