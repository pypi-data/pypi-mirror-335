"""Module for Batch Posting Window."""
import re
import time
import contextlib
from decimal import Decimal

import _ctypes
import pyautogui
from retry import retry
from t_desktop.config import IS_WINDOWS_OS

if IS_WINDOWS_OS:
    from pywinauto.keyboard import send_keys
    from pywinauto.controls.uia_controls import ListItemWrapper
    from pywinauto.application import WindowSpecification
    from pywinauto.findwindows import ElementNotFoundError
from t_desktop.decorators import retry_if_pywin_error
from t_nextgen.nextgen_window import NextGenWindow
from t_nextgen.constants import CONST
from t_nextgen.exceptions import (
    NoMatchingBatchDescriptionException,
    NextGenDuplicateImportException,
    BatchFromBarNotFound,
)


class BatchPostingWindow(NextGenWindow):
    """Batch Posting Class with methods to interact with batch posting window."""

    @property
    def window(self):
        """Return the AMBatches window element."""
        self.desktop_app.dialog.child_window(auto_id="NGEPMBatchLookup", control_type="Window").wait("visible", 5)
        return self.desktop_app.dialog.child_window(auto_id="NGEPMBatchLookup", control_type="Window")

    @property
    def batch_posting_window(self):
        """Return the BatchPosting window element."""
        return self.desktop_app.dialog.child_window(title="BatchPosting", control_type="Window")

    @retry(tries=3, delay=2)
    def click_batch_icon_from_bar(self, practice_name: str) -> None:
        """Clicks the Batch Posting button from the menu bar."""
        try:
            self.logger.debug("Clicking on the batch icon from the bar.")
            batch_icon = self.desktop_app.dialog.child_window(auto_id="cmdToolPosting")
            self.desktop_app.mouse_click_element(batch_icon)
            self.desktop_app.safe_wait({"auto_id": "Data Area", "control_type": "Custom", "found_index": 0})
            self.maximize_batch_window()
        except _ctypes.COMError:
            pass
        except TimeoutError as e:
            self.desktop_app.deal_with_unhandled_exception_popup(f"NextGen - {practice_name}")
            raise e
        except ElementNotFoundError:
            raise BatchFromBarNotFound("Element with auto_id: cmdToolPosting, not found")

    def click_batch_from_window_menu_if_exist(self) -> bool:
        """This method clicks on the batch from the window menu.

        Returns:
            bool: True if the window menu is found, False otherwise
        """
        windows_menu = self.desktop_app.dialog.child_window(title="Window", control_type="MenuItem")
        windows_menu.set_focus()
        windows_menu.select()
        try:
            windows_menu.child_window(title="1 Batch Posting", control_type="MenuItem").select()
            self.logger.debug("Clicked on the batch from the window menu")
            return True
        except _ctypes.COMError:
            return True
        except ElementNotFoundError:
            return False

    def _deal_with_no_batch_found_popup(self) -> None | NoMatchingBatchDescriptionException:
        modal = self.desktop_app.dialog.child_window(title="NextGen", control_type="Window")
        if modal.exists(timeout=3, retry_interval=1):
            self.logger.debug("No batch found. Closing popup")
            send_keys("{ENTER}")
            send_keys("%C")
            raise NoMatchingBatchDescriptionException(CONST.BATCH_DESCRIPTION_NOT_FOUND)
        return None

    def _set_amount_field_in_batch_lookup(self, search_criteria_window: WindowSpecification, amount: Decimal) -> None:
        self.logger.debug(f"Setting amount field in batch lookup to {amount}")
        amount_field = search_criteria_window.child_window(auto_id="txtAmount", control_type="Edit")
        amount_field.set_focus()
        with contextlib.suppress(_ctypes.COMError):
            amount_field.set_text(amount)

    def run_batch_lookup(self, trn: str, amount: Decimal, fill_amount: bool = False) -> None | ListItemWrapper:
        """Performs a batch lookup based on the provided criteria.

        Args:
            trn (str): The batch description to search for.
            amount (Decimal): The amount associated with the batch, used to filter the results.
            fill_amount (bool): If True, fills in the amount field in the search interface before performing the search.
                                Default is False.

        Returns:
            None | ListItemWrapper: Returns the matching item if exactly one batch is found.
            Otherwise, raises an exception.

        Raises:
            NoMatchingBatchDescriptionException: If no matching batch is found.
            NextGenDuplicateImportException: If more than one matching batch is found.
        """
        self.logger.info(f"Running batch lookup: trn={trn}, amount={amount}")
        self.click_menu_icon("a")
        search_criteria_window = self.window.child_window(auto_id="grpSearchCriteria")
        if fill_amount:
            self._set_amount_field_in_batch_lookup(search_criteria_window, amount)
        description_field = search_criteria_window.child_window(auto_id="txtDesc", control_type="Edit")
        description_field.set_focus()
        with contextlib.suppress(_ctypes.COMError):
            description_field.set_text(trn)
        send_keys("%F")

        self._deal_with_no_batch_found_popup()

        tree_view = self.window.child_window(auto_id="ColScrollRegion: 0, RowScrollRegion: 0")

        data_items = self._get_column_data_from_rows(tree_view, "Description")
        if data_items is None:
            send_keys("%C")
            self.logger.debug("No matching batch description found")
            raise NoMatchingBatchDescriptionException(CONST.BATCH_DESCRIPTION_NOT_FOUND)

        rows = self._filter_rows(data_items, trn, amount)
        rows_count = len(rows)
        if rows_count == 1:
            if not rows[0]["Visible"]:
                self._click_down_n_times(rows[0]["index"])
                rows[0]["Visible"] = True
            with contextlib.suppress(_ctypes.COMError):
                rows[0]["EditWrapper"].click_input()
            self.logger.info("Batch row found")
            return rows[0]["element"]
        elif rows_count == 0:
            send_keys("%C")
            raise NoMatchingBatchDescriptionException(CONST.BATCH_DESCRIPTION_NOT_FOUND)
        else:
            send_keys("%C")
            self.logger.debug("More than one batch with the same description was found")
            raise NextGenDuplicateImportException("More than one batch with the same description was found")

    def click_menu_icon(self, key: str) -> None:
        """Clicks the menu icon button in the 'Batch Posting' window.

        Args:
            batch_window (WindowSpecification): The 'Batch Posting' window object.
            key (str): The key to send after clicking the button.
        """
        self.logger.debug("Clicking the menu icon button in the 'Batch Posting' window")
        self.batch_window = self._get_batch_window()
        cmd_drill_button = self.batch_window.child_window(title="cmdDrill", control_type="Button")
        with contextlib.suppress(_ctypes.COMError):
            cmd_drill_button.click_input()
        time.sleep(1)

        send_keys(key)

    @retry(tries=3, delay=1)
    def _get_batch_window(self) -> WindowSpecification:
        """Retrieves the 'Batch Posting' window.

        Returns:
            WindowSpecification: The 'Batch Posting' window object.
        """
        self.logger.debug("Getting the 'Batch Posting' window")
        self.desktop_app.wait_until_element_visible(control_type="Window", title="BatchPosting", timeout=15)
        self.desktop_app.wait_until_element_visible(control_type="Pane", title="lstListing", timeout=15)
        batch_window = self.desktop_app.dialog.child_window(title="BatchPosting", control_type="Window")
        return batch_window

    def _get_column_data_from_rows(self, rows_list: ListItemWrapper, column_name: str) -> list[dict]:
        """The function retrieves information about data items in a tree view.

        :param rows_list: The `rows_list` parameter is the object representing the tree view control in
        the user interface. It is used to access the elements and descendants of the tree view
        :param column_name: The `column_name` parameter is a string that represents the name of the
        column in the tree view that you want to retrieve data from
        :return: a list of dictionaries, where each dictionary represents a data item in a tree view.
        Each dictionary contains information about the data item, such as its text, visibility, the
        value of a specified column, and an edit wrapper object.
        """
        column_data_rows = []
        all_descendants = rows_list.descendants()

        index = 0
        for element in all_descendants:
            if "DataItem" in element.element_info.control_type:
                index += 1
                data_item_info = {
                    "Text": element.element_info.name,
                    "Visible": element.is_visible(),
                    column_name: None,
                    "EditWrapper": None,
                    "index": index,
                    "element": element,
                }

                data_item_descendants = element.descendants()
                edit_controls = [
                    descendant
                    for descendant in data_item_descendants
                    if "Edit" in descendant.element_info.control_type and column_name in descendant.element_info.name
                ]

                if edit_controls:
                    description_edit = edit_controls[0]
                    data_item_info[column_name] = description_edit.get_value()
                    data_item_info["EditWrapper"] = description_edit
                column_data_rows.append(data_item_info)
        return column_data_rows

    def _filter_rows(self, dicts: list[dict], description: str, amt: Decimal) -> list[dict]:
        """Check for duplicates in a list of dictionaries based on a given description.

        Args:
            dicts (list[dict]): A list of dictionaries to search through.
            description (str): The description to match within each dictionary.
            amt (Decimal): Amount from the payment object

        Returns:
            list[dict]: A list of dictionaries where the description matches the given description.
        """
        result = []
        for d in dicts:
            if "Description" in d and description in d["Description"]:
                amt_extracted = self._extract_amt_from_description(d["Description"])
                if amt_extracted is None:
                    self.logger.info("Unable to determine amount value from batch description")
                elif amt == Decimal(amt_extracted):
                    result.append(d)
        return result

    def _extract_amt_from_description(self, description: str) -> None | str:
        """Extract amount from batch description in nextgen.

        Args:
            description (str): The description from which we want the amount.

        Returns
            (str): The amount extracted.
        """
        # Find the amount with optional commas and dollar sign
        match = re.search(r"\$\s?([\d,]+\.?\d*)", description)
        if match:
            # Extract the numeric part and replace commas
            amount_str = match.group(1).replace(",", "")
            self.logger.debug(f"Extracted amount from description: {amount_str}")
            return amount_str
        return None

    def _click_down_n_times(self, n: int, confidence_value: int = 3) -> None:
        """This method clicks the down key n times.

        Args:
            n (int): The number of times to click the down key.
            confidence_value (int, optional): confidence value. Defaults to 3.
        """
        self.logger.debug(f"Clicking down {n + confidence_value} times")
        pyautogui.press("home")
        for _ in range(n + confidence_value):
            pyautogui.press("down")

    def check_boxes_in_batch_posting(self, current_phase: str) -> None:
        """Toggle the state of three checkboxes in a batch posting dialog.

        Toggles the state of checkboxes with auto_ids "_chkSecure_0", "_chkSecure_1", and "_chkSecure_2"
        in the current dialog.

        Args:
            current_phase: the current phase of the work item
        """

        @retry(tries=3, delay=3)
        def toggle_checkbox(checkbox, untoggle: bool = False):
            """This method toggle the checkbox and prevents the useless COMError.

            This also wraps the necessity of using one Try-Except for each checkbox

            Args:
                checkbox (pywinauto.controls.uia_controls.CheckBoxWrapper): checkbox object
                untoggle (bool): untoggle the checkbox if True
            """
            with contextlib.suppress(_ctypes.COMError):
                toggle_value = 1 if untoggle else 0
                if checkbox.get_toggle_state() == toggle_value:
                    checkbox.toggle()

        checkbox_ids = ["_chkSecure_0", "_chkSecure_1", "_chkSecure_2"]
        checkboxes = []
        checkboxes.append(
            self.desktop_app.dialog.child_window(auto_id=checkbox_ids[0], control_type="CheckBox").wait("visible", 10)
        )
        for checkbox_id in checkbox_ids:
            checkboxes.append(self.desktop_app.dialog.child_window(auto_id=checkbox_id, control_type="CheckBox"))

        for checkbox in checkboxes:
            untoggle = False
            if checkbox == "_chkSecure_0" and current_phase == CONST.WORK_ITEM_PHASE.RETRY.value:
                untoggle = True
            toggle_checkbox(checkbox, untoggle)

    @retry(tries=3, delay=3)
    def set_focus_in_batch_window(self):
        """This method sets the focus in the batch window."""
        self.logger.debug("Setting focus in the batch window")
        window = self.desktop_app.dialog.child_window(title="BatchPosting", control_type="Window")
        pane = window.child_window(auto_id="lstListing")
        div = pane.child_window(auto_id="Data Area", control_type="Custom", found_index=0)
        tree_view = div.child_window(auto_id="ColScrollRegion: 0, RowScrollRegion: 0")
        self.desktop_app.mouse_click_element(tree_view)

    @retry(tries=3, delay=3)
    def click_ok_quick_batch(self) -> None:
        """The function clicks on the "OK" button in the Quick Batch dialog window."""
        self.logger.debug("Clicking on the OK button in the Quick Batch dialog window")
        ok_button = self.desktop_app.dialog.child_window(title="cmdOK", control_type="Button")
        with contextlib.suppress(_ctypes.COMError):
            ok_button.click()

    @staticmethod
    def click_quick_batch_from_batch_menu(quick_batch_position: int = 2) -> None:
        """The function clicks on the "Quick Batch" option in the batch menu."""
        for _ in range(quick_batch_position):
            send_keys("{DOWN}")
        send_keys("{ENTER}")

    @staticmethod
    def click_new_from_batch_menu(new_batch_item_position: int = 1) -> None:
        """The function clicks on the "New..." option in the batch menu.

        Args:
            new_batch_item_position (int): the position of the "New..." option in the batch menu
        """
        for _ in range(new_batch_item_position):
            send_keys("{DOWN}")
        send_keys("{RIGHT}")

    def maximize_batch_window(self) -> None:
        """This method maximizes the batch window."""
        try:
            if not self.batch_posting_window.was_maximized():
                self.logger.debug("Maximizing the batch window")
                self.batch_posting_window.maximize()
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Could not maximize the batch window: {str(e)}")

    def get_batch_row(self, trn: str, amount: str) -> None | ListItemWrapper:
        """This method retrieves the batch row in the batch posting dialog that matches the given description.

        Args:
            description (str): The description to match against the batch posting dialog.
            amount (str): The amount to match against the batch posting dialog.

        Returns:
            None | ListItemWrapper: The batch row that matches the given description.

        Raises:
            NoMatchingBatchDescription: If no matching description is found.
            NextGenDuplicateImportException: If multiple matching descriptions are found.
        """
        div = self.desktop_app.dialog.child_window(auto_id="Data Area", control_type="Custom", found_index=0)
        tree_view = div.child_window(auto_id="ColScrollRegion: 0, RowScrollRegion: 0")
        data_items = self._get_column_data_from_rows(tree_view, "Description")

        if data_items is None:
            raise NoMatchingBatchDescriptionException(CONST.BATCH_DESCRIPTION_NOT_FOUND)

        rows = self._filter_rows(data_items, trn, Decimal(amount))
        rows_count = len(rows)

        if rows_count == 1:
            if not rows[0]["Visible"]:
                self._click_down_n_times(rows[0]["index"])
                rows[0]["Visible"] = True
            with contextlib.suppress(_ctypes.COMError):
                rows[0]["EditWrapper"].click_input()
            return rows[0]["element"]
        elif rows_count == 0:
            raise NoMatchingBatchDescriptionException(CONST.BATCH_DESCRIPTION_NOT_FOUND)
        else:
            raise NextGenDuplicateImportException("More than one batch with the same description was found")

    def close_batch_look_up_window(self) -> None:
        """Click close button in Batch Lookup Window."""
        self.logger.debug("Closing the Batch Lookup window")
        batch_lookup_window = self.desktop_app.dialog.child_window(title="Batch Lookup", control_type="Window")
        batch_lookup_window.set_focus()
        with contextlib.suppress(_ctypes.COMError):
            batch_lookup_window.child_window(title="Close", control_type="Button", found_index=0).click_input()

    @retry_if_pywin_error()  # type: ignore[misc]
    def get_batch_date(self) -> str:
        """This function gets the batch date.

        Returns:
            str: Batch date
        """
        batch_date = (
            self.window.child_window(auto_id="ColScrollRegion: 0, RowScrollRegion: 0")
            .child_window(control_type="DataItem")
            .child_window(title="Date", control_type="Edit")
            .get_value()
        )
        self.logger.debug(f"Batch date: {batch_date}")
        return batch_date

    def get_batch_id(self) -> str:
        """This function gets the batch ID in the batch lookup flow.

        Returns:
            str: Batch ID
        """
        batch_id = (
            self.window.child_window(auto_id="ColScrollRegion: 0, RowScrollRegion: 0")
            .child_window(control_type="DataItem")
            .child_window(title="ID", control_type="Edit")
            .get_value()
        )
        self.logger.debug(f"Batch ID: {batch_id}")
        return batch_id

    def enter_quick_batch_name(self, name: str) -> None:
        """The function enters a Bach name into a text field in the Quick Batch dialog window.

        Args:
            name (str): the name of the batch
        """
        self.logger.debug(f"Entering quick batch name: {name}")
        quick_batch_window = self.desktop_app.dialog.child_window(auto_id="NGEPMQuickBatch", control_type="Window")
        batch_name_field = quick_batch_window.child_window(auto_id="txtDesc", control_type="Edit")
        batch_name_field.wait("visible", 5)
        with contextlib.suppress(_ctypes.COMError):
            batch_name_field.set_edit_text(name)

    @retry_if_pywin_error(3, 3)  # type: ignore[misc]
    def press_l_to_open_ledger_in_dropdown(self) -> None:
        """Press "l" to open the ledger in the opened dropdown."""
        self.logger.debug("Pressing 'l' to open the ledger in the dropdown")
        send_keys("l")
        self.desktop_app.dialog.child_window(title="BatchLedger", control_type="Window").wait("visible", 10)

    def _open_dropdown_for_batch_row(self) -> None:
        """Click on the ledger left button to open the options dropdown for the selected row."""
        self.logger.debug("Opening the options dropdown for the selected row")
        button = self.desktop_app.dialog.child_window(title="cmdDrill", control_type="Button")
        with contextlib.suppress(_ctypes.COMError):
            button.click()
        time.sleep(2)
