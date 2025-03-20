# coding:utf-8

from requests import Response


class StreamResponse():
    CHUNK_SIZE: int = 1048576  # 1MB

    def __init__(self, response: Response) -> None:
        self.__response: Response = response

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def generator(self):
        for chunk in self.response.iter_content(chunk_size=self.CHUNK_SIZE):
            yield chunk
