from playwright.sync_api import Expect, Page, Locator, APIResponse
from typing import Optional, Union, overload
from bugster.core.base_page import BugsterPage
from bugster.core.custom_locator import BugsterLocator
from playwright.sync_api._generated import (
    PageAssertions,
    LocatorAssertions,
    APIResponseAssertions,
)
from playwright._impl._assertions import (
    PageAssertions as PageAssertionsImpl,
    LocatorAssertions as LocatorAssertionsImpl,
)
import time


class BugsterExpect(Expect):
    @overload
    def __call__(
        self, actual: BugsterPage, message: Optional[str] = None
    ) -> PageAssertions: ...

    @overload
    def __call__(
        self, actual: BugsterLocator, message: Optional[str] = None
    ) -> LocatorAssertions: ...

    def __call__(
        self,
        actual: Union[BugsterPage, BugsterLocator, Page, Locator, APIResponse],
        message: Optional[str] = None,
    ) -> Union[PageAssertions, LocatorAssertions, APIResponseAssertions]:
        if hasattr(actual, "_step_delay") and actual._step_delay > 0:
            time.sleep(6)

        if isinstance(actual, BugsterPage):
            assertions = PageAssertions(
                PageAssertionsImpl(actual._impl_obj, self._timeout, message=message)
            )
            if actual.screenshot:
                actual.screenshot_step(name="after_expect")
            return assertions
        elif isinstance(actual, BugsterLocator):
            assertions = LocatorAssertions(
                LocatorAssertionsImpl(actual._impl_obj, self._timeout, message=message)
            )
            if actual._page.screenshot:
                actual._page.screenshot_step(name="after_expect")
            return assertions
        # If we implement BugsterAPIResponse in the future, we will need to add this elif block
        # elif isinstance(actual, BugsterAPIResponse):
        #     return APIResponseAssertions(
        #         APIResponseAssertionsImpl(actual._impl_obj, self._timeout, message=message)
        #     )
        else:
            return super().__call__(actual, message)


expect = BugsterExpect()
