import tempfile
from collections import deque
from concurrent.futures import as_completed
from datetime import datetime
from pathlib import Path

from backend.logger import log
from backend.merging import Merging
from backend.repak import Repak
from backend.utilities import Files
from config.settings_manager import settings
from config.translations import translate
from gui.window_messagebox import ModalFileDialog, WindowMessageBox


class ConflictProcessor:
    """Handles file processing, unpacking, and merging logic."""

    def __init__(self, master, ignore_no_conflicts):
        self.master = master
        self.tree = master.tree
        self.ignore_no_conflicts = ignore_no_conflicts
        self.processed_conflicts = deque()
        self.not_processed = deque()

    def process_selected_files(self):
        merging_engine = settings.MERGING_ENGINE
        tool_paths = settings.TOOLS_PATHS
        if merging_engine == "WinMerge":
            engine_path = Path(tool_paths.get("winmerge"))
        elif merging_engine == "KDiff3":
            engine_path = Path(tool_paths.get("kdiff3"))
        if not Files.is_existing_file_type(engine_path, ".exe"):
            log.error(f"{merging_engine} executable isn't found at {str(engine_path)}")
            return "error", (
                f'{merging_engine} executable {translate("error_executable_not_found_1")} {str(engine_path)}\n{translate("error_executable_not_found_2")}'
            )

        selected_items = self.tree.selection()
        if not selected_items:
            return "warning", (translate("merge_screen_conflicts_select_files"))

        self.processed_conflicts = deque()
        self.not_processed = deque()

        with tempfile.TemporaryDirectory() as temp_merging_dir:
            temp_merging_dir = Path(temp_merging_dir)
            for item_id in selected_items:
                try:
                    item = self.tree.item(item_id)
                    item_tags = item["tags"]
                    item_name = item["text"]

                    item_values = item.get("values", [])

                    if len(item_values) < 3:
                        log.warning(
                            f"Item '{item_name}' ({item_id}) has insufficient values: {item_values}"
                        )
                        self.not_processed.append(f"{item_name} (invalid values)")
                        continue

                    if not item_values[0] or not item_values[1] or not item_values[2]:
                        log.debug(
                            f"Item '{item_name}' ({item_id}) is probably not a file, skipping."
                        )
                        continue

                    item_sources_names = item_values[0].split(", ")
                    item_sources_paths = item_values[1].split(", ")
                    item_path = Path(item_values[2])

                    log.debug(f"Starting to process {item_name}...")
                    log.debug(f"{item_name} tags: {item_tags}...")
                    log.debug(f"{item_name} internal path: {item_path}...")
                    log.debug(f"{item_name} sources paths: {item_sources_paths}...")

                    if "no_conflicts" in item_tags:
                        if self.ignore_no_conflicts:
                            log.debug(f"{item_name} skipped (no conflicts)")
                            self.not_processed.append(f"{item_name} (no conflicts)")
                        else:
                            self._unpack_and_merge(
                                item_name,
                                item_sources_paths,
                                item_sources_names,
                                item_path,
                                temp_merging_dir,
                                True,
                            )
                    elif "dual_match" in item_tags:
                        self._unpack_and_merge(
                            item_name,
                            item_sources_paths,
                            item_sources_names,
                            item_path,
                            temp_merging_dir,
                            True,
                        )
                    elif "dual_no_match" in item_tags:
                        self._unpack_and_merge(
                            item_name,
                            item_sources_paths,
                            item_sources_names,
                            item_path,
                            temp_merging_dir,
                        )
                    elif "tri" in item_tags:
                        self._unpack_and_merge(
                            item_name,
                            item_sources_paths,
                            item_sources_names,
                            item_path,
                            temp_merging_dir,
                        )
                    elif "complex" in item_tags:
                        log.debug(f"{item_name} skipped (too much sources)")
                        self.not_processed.append(f"{item_name} (too much sources)")
                    else:
                        log.debug(f"{item_name} skipped (ineligible for merging)")
                        self.not_processed.append(
                            f"{item_name} (ineligible for merging)"
                        )

                except KeyError as e:
                    log.exception(f"Missing key for item '{item_name}': {e}")
                    self.not_processed.append(f"{item_name} (missing key)")
                except Exception as e:
                    log.exception(f"Error processing '{item_name}': {e}")
                    self.not_processed.append(f"{item_name} (processing error)")

            if not self.processed_conflicts and self.not_processed:
                not_processed_str = "\n".join(map(str, self.not_processed))
                not_processed_str2 = ", ".join(map(str, self.not_processed))
                log.warning("No files were processed!")
                log.debug(f"Skipped files: {not_processed_str2}")
                return "info", (
                    [
                        f'{translate("merge_screen_conflicts_no_files_processed")}\n\n{translate("merge_screen_conflicts_final_report_3")}',
                        not_processed_str,
                    ]
                )

            elif Files.is_folder_empty(temp_merging_dir):
                return "error", (translate("merge_dir_is_empty"))
            else:
                folder_to_place_merged_mod = self._insistent_askdirectory(
                    parent=self.master
                )
                if folder_to_place_merged_mod:

                    formatted_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    merged_mod_path = (
                        folder_to_place_merged_mod
                        / f"z_zonepaq_merged_{formatted_time}_P.pak"
                    )

                    log.info(
                        f"Repacking: {str(temp_merging_dir)} into {str(folder_to_place_merged_mod)}"
                    )
                    future = Repak.repack(
                        temp_merging_dir, forced_destination=merged_mod_path
                    )

                    try:
                        repack_success, repak_result = future.result()

                        if repack_success:
                            processed_str = "\n".join(
                                map(str, self.processed_conflicts)
                            )
                            not_processed_str = "\n".join(map(str, self.not_processed))
                            return "info", (
                                [
                                    f'{translate("merge_screen_conflicts_final_report_1")}\n{repak_result}',
                                    "",
                                    translate("merge_screen_conflicts_final_report_2"),
                                    processed_str or translate("generic_none"),
                                    translate("merge_screen_conflicts_final_report_3"),
                                    not_processed_str or translate("generic_none"),
                                ]
                            )

                        else:
                            return "error", (
                                [
                                    f'{translate("merge_screen_conflicts_final_report_1")}\n{repak_result}',
                                    "",
                                    translate("merge_screen_conflicts_final_report_2"),
                                    processed_str or translate("generic_none"),
                                    translate("merge_screen_conflicts_final_report_3"),
                                    not_processed_str or translate("generic_none"),
                                ]
                            )

                    except Exception as e:
                        log.exception(f"Unexpected error during repack: {str(e)}")
                        return "error", (
                            [
                                translate("merge_screen_conflicts_repak_error"),
                                str(e),
                            ]
                        )

                else:
                    return "warning", (translate("merge_screen_conflicts_aborted"))

    def _unpack_and_merge(
        self,
        item_name,
        item_sources_paths,
        item_sources_names,
        item_path,
        temp_merging_dir,
        use_vanilla=False,
    ):

        with tempfile.TemporaryDirectory() as temp_unpack_dir:
            temp_dir_path = Path(temp_unpack_dir)
            unpacked_files = self.unpack_files(
                item_sources_paths, item_sources_names, item_path, temp_dir_path
            )
            self._merge_files(
                unpacked_files,
                item_name,
                item_path,
                temp_merging_dir,
                use_vanilla,
            )

    def unpack_files(
        self, item_sources_paths, item_sources_names, item_path, temp_dir_path
    ):
        unpacked_files = deque()
        futures = {}

        for i, item_source_path in enumerate(item_sources_paths):
            item_source_path = str(Path(item_source_path))
            future = Repak.unpack(item_source_path, temp_dir_path)
            futures[future] = (i, item_source_path)

        for future in as_completed(futures):
            i, item_source_path = futures[future]
            try:
                unpack_success, unpacked_folder = future.result()
                if unpack_success:
                    unpacked_file = Path(unpacked_folder) / item_path
                    if unpacked_file.exists() and unpacked_file.is_file():
                        unpacked_files.append(unpacked_file)
                    else:
                        log.warning(f"Unpacked file does not exist: {unpacked_file}")
                else:
                    log.error(f"Unpack failed for {item_source_path}")
            except FileNotFoundError as e:
                log.exception(
                    f"File not found: {item_sources_names[i]} -> {item_source_path}: {e}"
                )
            except Exception as e:
                log.exception(
                    f"Unexpected error unpacking {item_sources_names[i]}: {e}"
                )

        return unpacked_files

    def _merge_files(
        self, unpacked_files, item_name, item_path, temp_merging_dir, use_vanilla=False
    ):
        if not unpacked_files:
            log.error(f"No valid files to compare for {str(item_path)}")
            return

        save_path = temp_merging_dir / item_path
        Files.create_dir(save_path.parent)

        if use_vanilla:
            from backend.games_manager import GamesManager

            for item in GamesManager.vanilla_files:
                unpacked_folder = item["unpacked"]
                vanilla_file = Path(unpacked_folder) / item_path

                if vanilla_file.exists() and vanilla_file.is_file():
                    unpacked_files.appendleft(vanilla_file)

        compare_success, compare_result = Merging._run_engine(unpacked_files, save_path)

        log.debug(
            f"{settings.MERGING_ENGINE} returned with code {compare_result.returncode}"
        )

        file_exists = Files.is_existing_file(save_path)

        if compare_success and compare_result.returncode == 0 and file_exists:
            log.info(f"Merging successful for {str(item_path)}")
            self.processed_conflicts.append(item_name)
        else:
            if not file_exists:
                log.error(f"{str(item_path)} wasn't saved in {settings.MERGING_ENGINE}")
                self.not_processed.append(
                    f"{item_name} (wasn't saved in {settings.MERGING_ENGINE})"
                )
            else:
                log.error(
                    f"Merging failed for {str(item_path)}: {compare_result.stderr}"
                )
                self.not_processed.append(
                    f"{item_name} ({settings.MERGING_ENGINE} returned: {compare_result.stderr})"
                )

    def _insistent_askdirectory(self, parent, initialdir=None, title=None):
        folder_selected = None
        while True:
            folder_selected = ModalFileDialog.askdirectory(
                parent=parent, initialdir=initialdir, title=title
            )

            if folder_selected:
                return Path(folder_selected)
            else:
                retry = WindowMessageBox.askretrycancel(
                    parent,
                    message=translate(
                        "merge_screen_conflicts_select_merged_destination"
                    ),
                )
                if not retry:
                    return None
