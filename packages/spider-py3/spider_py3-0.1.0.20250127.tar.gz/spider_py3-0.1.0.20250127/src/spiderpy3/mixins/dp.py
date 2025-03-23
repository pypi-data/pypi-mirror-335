import atexit
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.items import ChromiumTab, ChromiumElement
from DrissionPage.errors import ElementNotFoundError, NoRectError
from typing import Any, Optional, Union, Dict, Literal, Callable


class DpMixin(object):
    def __init__(
            self,
            cp_kwargs: Optional[Dict[str, Any]] = None,
            ct_kwargs: Optional[Dict[str, Any]] = None,
            mode: Literal["cp", "ct"] = "ct",
            dp: Union[None, ChromiumTab, ChromiumPage] = None,
            close_dp: bool = True,
    ) -> None:
        self.cp_kwargs = dict(
            addr_or_opts=self.get_co(),
            tab_id=None
        )
        if cp_kwargs is not None:
            self.cp_kwargs.update(cp_kwargs)

        self.ct_kwargs = dict(
            url=None,
            new_window=False,
            background=False,
            new_context=False
        )
        if ct_kwargs is not None:
            self.ct_kwargs.update(ct_kwargs)

        self.mode = mode

        self._dp = dp

        self.close_dp = close_dp

        atexit.register(self.close)

    @staticmethod
    def get_co() -> ChromiumOptions:
        co = ChromiumOptions()
        co.auto_port()
        co.set_argument("--window-size=500,500")
        # co.set_argument("--start-fullscreen")
        # co.set_argument("--start-maximized")
        return co

    @staticmethod
    def create_cp(**kwargs: Dict[str, Any]) -> ChromiumPage:
        cp = ChromiumPage(**kwargs)
        return cp

    @staticmethod
    def create_ct(cp: ChromiumPage, **kwargs: Dict[str, Any]) -> ChromiumTab:
        ct = cp.new_tab(**kwargs)
        return ct

    @property
    def dp(self) -> Union[ChromiumPage, ChromiumTab]:
        if self._dp is None:
            if self.mode == "cp":
                self._dp = self.create_cp(**self.cp_kwargs)
            elif self.mode == "ct":
                cp = self.create_cp(**self.cp_kwargs)
                close_tab_id = cp.tab_id if cp.tabs_count == 1 and cp.url == "chrome://newtab/" else None
                self._dp = self.create_ct(cp, **self.ct_kwargs)
                if close_tab_id is not None:
                    cp.close_tabs(close_tab_id)
        return self._dp

    def close(self) -> None:
        if self.close_dp is True and self._dp is not None:
            if isinstance(self._dp, ChromiumPage):
                self._dp.close()
                self._dp.quit()
            elif isinstance(self._dp, ChromiumTab):
                self._dp.close()
            self._dp = None

    def __enter__(self) -> Union[ChromiumPage, ChromiumTab]:
        return self.dp

    def __exit__(self, exc_type, exc_value, traceback) -> Optional[bool]:
        self.close()
        return False

    @staticmethod
    def do_if_ele_not_is_in_viewport(ele: ChromiumElement, do: Callable) -> None:
        try:
            assert ele.states.is_in_viewport is True
        except (ElementNotFoundError, NoRectError, AssertionError):  # todo: 添加更多异常
            do()

    def wait(self, dp: Union[ChromiumPage, ChromiumTab, None] = None, timeout: Optional[float] = None) -> None:
        if dp is None:
            dp = self.dp
        dp.wait.load_start(timeout)
        dp.wait.doc_loaded(timeout)

    def get_by_run_js(
            self, url: str,
            dp: Union[ChromiumPage, ChromiumTab, None] = None,
            timeout: Optional[float] = None
    ) -> None:
        if dp is None:
            dp = self.dp
        dp.run_js(f"""location.href = '{url}';""")
        self.wait(dp, timeout)

    def click_by_run_js(
            self, xpath: str,
            dp: Union[ChromiumPage, ChromiumTab, None] = None,
            timeout: Optional[float] = None
    ) -> None:
        if dp is None:
            dp = self.dp
        js = f"document.evaluate('{xpath}',document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue?.click();"  # noqa: E501
        dp.run_js(js)
        self.wait(dp, timeout)
