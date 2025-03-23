from abc import abstractmethod
from typing import Any, Optional

from spiderpy3.objects.object import Object


class Handler(Object):
    @abstractmethod
    def action(self, *args, **kwargs) -> Any:
        pass

    def run_ok_method(self, result: Any) -> Any:
        pass

    def run_error_method(self, e: Exception) -> Optional[bool]:
        """

        :param e:
        :return: None，则抛出异常
                 True，忽略异常且无日志
                 False，忽略异常但有日志
        """
        pass

    def run(self, *args, **kwargs) -> Any:
        try:
            result = self.action(*args, **kwargs)
        except Exception as e:
            ret = self.run_error_method(e)
            if ret is None:
                raise e
            if ret is True:
                pass
            if ret is False:
                self.logger.exception(e)
        else:
            self.run_ok_method(result)
            return result

    def loop_run(self, *args, **kwargs) -> None:
        run_times = 0
        while True:
            run_times += 1
            self.logger.debug(f"循环运行第{run_times}次开始")
            self.run(*args, **kwargs)
            self.logger.debug(f"循环运行第{run_times}次结束")
