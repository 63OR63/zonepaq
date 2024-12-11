import tempfile
import tkinter as tk
from collections import deque
from concurrent.futures import as_completed
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from backend.logger import log
from backend.tools import Files, Merging, Repak
from config.metadata import APP_NAME
from config.settings import settings, translate
from gui.widgets import CustomButton, CustomEntry


class GUI_Popup:
    """Base class for creating popup windows with custom configurations."""

    def __init__(self, parent, title, geometry="800x400"):
        self.root = parent
        self.window = tk.Toplevel(self.root)
        self.window.title(f"{APP_NAME} - {title}")
        self.window.geometry(geometry)
        self.window.resizable(False, False)
        self.window.configure(bg=settings.THEME_DICT["color_background"])
        self.root.customization_manager.instances.register_window(self.window)
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

    def _close_window(self):
        self.root.customization_manager.instances.unregister_window(window=self.window)
        self.window.destroy()


class GUI_SettingsMenu(GUI_Popup):
    """Popup window for configuring and saving application settings."""

    def __init__(self, parent):
        super().__init__(
            parent=parent,
            title=translate("menu_preferences_settings"),
            geometry="800x400",
        )
        self.padding = self.root.padding
        self.temp_paths = {}  # Temporary storage for paths
        self._add_settings_groups()
        self._add_save_button()
        self.root.adjust_to_content(root=self.window, adjust_width=True)
        log.info("Settings menu opened.")

    def _add_settings_groups(self):
        # Configure columns to allow entry expansion
        self.window.grid_columnconfigure(1, weight=1)  # Column 1 for entries expands
        self.window.grid_columnconfigure(
            2, weight=0
        )  # Column 2 for buttons remains fixed

        header_label = ttk.Label(
            self.window,
            text=translate("menu_preferences_settings"),
            style="Header.TLabel",
        )
        header_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.window.grid_rowconfigure(0, weight=1)

        path_groups = {
            translate("menu_preferences_settings_path_tools"): [
                (settings.TOOLS_PATHS, "repak_cli", "repak"),
                (settings.TOOLS_PATHS, "winmerge", "WinMerge"),
                (settings.TOOLS_PATHS, "kdiff3", "kdiff3"),
            ],
            translate("menu_preferences_settings_path_game"): [
                (
                    settings.GAME_PATHS,
                    "vanilla_unpacked",
                    translate("menu_preferences_settings_vanilla_unpacked"),
                ),
            ],
        }

        row_index = 1
        for group_name, paths in path_groups.items():
            row_index = self._add_path_group(group_name, paths, row_index)

    def _add_path_group(self, group_name, paths, starting_row):
        self._create_group_label(group_name, starting_row)
        for index, (path_dict, path_key, path_title) in enumerate(
            paths, start=starting_row + 1
        ):
            self._create_path_input(path_dict, path_key, path_title, index)
        return starting_row + len(paths) + 1

    def _create_group_label(self, group_label, row):
        ttk.Label(
            self.window, text=f"{group_label}:", style="SettingsGroup.TLabel"
        ).grid(
            row=row,
            column=0,
            columnspan=3,
            padx=self.padding * 2,
            pady=(self.padding, self.padding / 2),
            sticky="w",
        )

    def _create_path_input(self, path_dict, path_key, path_title, row):
        # Label for the path
        ttk.Label(
            self.window, text=f"{path_title}:", style="SettingsItem.TLabel", anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=(self.padding, self.padding))

        # Path variable and settings logic
        path_variable = tk.StringVar(value=path_dict.get(path_key, ""))

        # Configure column weights
        self.window.grid_columnconfigure(1, weight=1)  # Entry column expands
        self.window.grid_columnconfigure(2, weight=0)  # Button column fixed

        # CustomEntry widget
        entry_widget = CustomEntry(
            parent=self.window,
            customization_manager=self.root.customization_manager,
            textvariable=path_variable,
            width=85,
            style=(
                "PathEntry.TEntry"
                if Path(path_dict.get(path_key, "").strip()).exists()
                else "PathInvalid.TEntry"
            ),
        )
        entry_widget.grid(row=row, column=1, sticky="ew", padx=(0, self.padding))

        # Browse Button with fixed size
        browse_button = CustomButton(
            parent=self.window,
            customization_manager=self.root.customization_manager,
            text=translate("menu_preferences_settings_browse"),
            command=lambda: self._open_path_browse_dialog(path_variable),
            style="TButton",
            width=100,  # Fixed width in pixels
            height=30,  # Fixed height in pixels
        )
        browse_button.grid(
            row=row, column=2, padx=(0, self.padding), pady=self.padding / 4, sticky="e"
        )

        # Add trace for validation
        path_variable.trace_add(
            "write",
            lambda *args: self._update_temp_path(
                path_key, path_variable.get(), entry_widget
            ),
        )

    def _update_temp_path(self, path_key, new_path, entry_widget):
        """Store temporary path changes in the temp_paths dictionary."""
        self.temp_paths[path_key] = new_path
        entry_widget.apply_style(
            forced_style=entry_widget.get_style()
        )  # Apply dynamic style change

    def _add_save_button(self):
        CustomButton(
            parent=self.window,
            text=translate("menu_preferences_settings_save"),
            command=self._save_settings_and_close,
            customization_manager=self.root.customization_manager,
            style="Accent.TButton",
            width=130,
            height=50,
        ).grid(
            row=self._get_highest_row() + 1,
            column=0,
            columnspan=3,
            pady=(self.padding, self.padding * 1.5),
        )

    def _get_highest_row(self):
        return max(widget.grid_info()["row"] for widget in self.window.grid_slaves())

    def _save_settings_and_close(self):
        # Save updated paths from temp_paths back to the corresponding path dictionaries
        path_groups = {
            "game": settings.GAME_PATHS,
            "tools": settings.TOOLS_PATHS,
        }

        # Loop through each group and update the paths
        for group_name, paths in path_groups.items():
            for path_key in paths.keys():
                if path_key in self.temp_paths:
                    # Update the path in the respective dictionary
                    paths[path_key] = self.temp_paths[path_key]

        # Save the updated settings to disk
        settings.save_settings()

        # Close the settings window
        self.window.destroy()

    def _open_path_browse_dialog(self, path_variable):
        selected_path = filedialog.askdirectory()
        if selected_path:
            path_variable.set(selected_path)


class GUI_ConflictsReport(GUI_Popup):
    """Displays conflict reports and provides tools to analyze and merge files."""

    def __init__(self, parent, content_tree):
        super().__init__(
            parent=parent,
            title=translate("merge_screen_conflicts_title"),
            geometry="800x400",
        )
        self.padding = self.root.padding
        self.content_tree = content_tree
        self.original_data = content_tree
        self.theme_dict = settings.THEME_DICT

        # Variable for checkbutton state
        self.show_full_paths = tk.BooleanVar(value=False)

        self.setup()
        self.root.adjust_to_content(
            root=self.window, adjust_width=True, adjust_height=False
        )
        log.info("Conflicts resolver screen menu opened.")

    def setup(self):
        self._create_search_frame()
        self._create_tree_frame()
        self._create_legend_frame()
        self._create_hints_frame()

    def _create_search_frame(self):
        search_frame = ttk.Frame(self.window, style="TFrame")
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        self._create_search_label(search_frame)
        self._create_search_entry(search_frame)
        self._create_show_paths_check_button(search_frame)

    def _create_search_label(self, search_frame):
        search_label = ttk.Label(
            search_frame, text=translate("generic_search"), style="TLabel"
        )
        search_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

    def _create_search_entry(self, search_frame):
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._search_tree())
        self.search_entry = CustomEntry(
            parent=search_frame,
            customization_manager=self.root.customization_manager,
            textvariable=self.search_var,
            style="PathEntry.TEntry",
            window=self.window,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5), pady=5)

    def _create_show_paths_check_button(self, search_frame):
        self.show_paths_check_button = ttk.Checkbutton(
            search_frame,
            text=translate("merge_screen_conflicts_show_path"),
            variable=self.show_full_paths,
            command=self._toggle_path_display,
            style="TCheckbutton",
        )
        self.show_paths_check_button.grid(row=0, column=2, padx=(5, 5))

    def _create_tree_frame(self):
        tree_frame = ttk.Frame(self.window, style="TFrame")
        tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self._create_treeview(tree_frame)
        self._create_scrollbar(tree_frame)

    def _create_treeview(self, tree_frame):
        self.tree = ttk.Treeview(
            tree_frame,
            style="Muted.Treeview",
            columns=("PAK Sources", "PAK Sources Paths", "File Path"),
            show="tree headings",
            height=15,
        )
        self._configure_treeview_headings()
        self._configure_treeview_columns()

        # Treeview Tag Configuration
        self.tree.tag_configure(
            "no_conflicts", foreground=self.theme_dict["color_success"]
        )
        self.tree.tag_configure(
            "dual_match", foreground=self.theme_dict["color_foreground"]
        )
        self.tree.tag_configure(
            "dual_no_match", foreground=self.theme_dict["color_attention"]
        )
        self.tree.tag_configure("tri", foreground=self.theme_dict["color_warning"])
        self.tree.tag_configure("complex", foreground=self.theme_dict["color_error"])

        self.conflict_counts = self._populate_tree("", self.content_tree)

    def _configure_treeview_headings(self):
        self.tree.heading(
            "#0", text=translate("merge_screen_conflicts_file_structure"), anchor="w"
        )
        self.tree.heading(
            "PAK Sources",
            text=translate("merge_screen_conflicts_pak_sources"),
            anchor="w",
        )
        self.tree.heading(
            "PAK Sources Paths",
            text=translate("merge_screen_conflicts_pak_sources_paths"),
            anchor="w",
        )

    def _configure_treeview_columns(self):
        self.tree.column("#0", stretch=False, width=360)
        self.tree.column("PAK Sources", stretch=True)
        self.tree.column(
            "PAK Sources Paths", width=0, stretch=tk.NO
        )  # Invisible column
        self.tree.column("File Path", width=0, stretch=tk.NO)  # Invisible column

    def _create_scrollbar(self, tree_frame):
        self.scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="nsw")

    def _create_legend_frame(self):
        legend_frame = ttk.Frame(self.window, style="TFrame")
        legend_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(self.padding, self.padding),
        )
        legend_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        legend_frame.grid_columnconfigure(1, weight=0)

        self._create_legend_labels(legend_frame)
        self._create_process_frame(legend_frame)

    def _create_legend_labels(self, legend_frame):
        self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_no_conflicts_count')} {self.conflict_counts['no_conflicts_count']}",
            style="Success.TLabel",
            row=1,
        )
        self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_dual_match_count')} {self.conflict_counts['dual_match_count']}",
            style="Small.TLabel",
            row=2,
        )
        self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_dual_no_match_count')} {self.conflict_counts['dual_no_match_count']}",
            style="Attention.TLabel",
            row=3,
        )
        self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_tri_count')} {self.conflict_counts['tri_count']}",
            style="Warning.TLabel",
            row=4,
        )
        self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_complex_count')} {self.conflict_counts['complex_count']}",
            style="Error.TLabel",
            row=5,
        )

    def _create_legend_label(self, legend_frame, text, style, row):
        hints_label = ttk.Label(legend_frame, text=text, style=style)
        hints_label.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=(self.padding, 0),
            pady=(0, self.padding / 4),
        )

    def _create_process_frame(self, legend_frame):
        process_frame = ttk.Frame(legend_frame, style="TFrame")
        process_frame.grid(
            row=1,
            column=1,
            rowspan=4,
            padx=(self.padding * 2, self.padding),
            sticky="ne",
        )

        self.ignore_no_conflicts = True
        self.ignore_no_conflicts_var = tk.BooleanVar(value=self.ignore_no_conflicts)

        self.ignore_no_conflicts_check_button = ttk.Checkbutton(
            process_frame,
            text=translate("merge_screen_ignore_no_conflicts_checkbutton"),
            variable=self.ignore_no_conflicts_var,
            command=self._toggle_ignore_no_conflicts,
            style="TCheckbutton",
        )
        self.ignore_no_conflicts_check_button.grid(
            row=0, column=0, pady=(0, self.padding / 2), sticky="ne"
        )

        buttons_frame = ttk.Frame(process_frame, style="TFrame")
        buttons_frame.grid(
            row=1,
            column=0,
            sticky="ne",
        )

        select_all_button = CustomButton(
            parent=buttons_frame,
            customization_manager=self.root.customization_manager,
            text=translate("merge_screen_conflicts_select_all_button"),
            command=lambda: self._select_tagged_items(),
            style="TButton",
            width=160,
            height=55,
            window=self.window,
        )
        select_all_button.grid(
            row=0,
            column=0,
            padx=(0, self.padding),
            sticky="ne",
        )

        process_button = CustomButton(
            parent=buttons_frame,
            customization_manager=self.root.customization_manager,
            text=translate("merge_screen_conflicts_action_button"),
            command=lambda: self._process_selected_files(),
            style="Accent.TButton",
            width=160,
            height=55,
            window=self.window,
        )
        process_button.grid(row=0, column=1, sticky="ne")

    def _select_tagged_items(self):
        self.tree.selection_remove(self.tree.selection())
        nodes_to_visit = deque(self.tree.get_children(""))

        while nodes_to_visit:
            item_id = nodes_to_visit.popleft()
            item = self.tree.item(item_id)
            item_tags = item.get("tags", [])

            if item_tags:
                self.tree.selection_add(item_id)

            nodes_to_visit.extend(self.tree.get_children(item_id))

    def _toggle_ignore_no_conflicts(self):
        self.ignore_no_conflicts = self.ignore_no_conflicts_var.get()

    def _create_hints_frame(self):
        if eval(settings.SHOW_HINTS):
            hints_frame = ttk.Frame(self.window, style="TFrame")
            hints_frame.grid(
                row=3,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=self.padding,
                pady=(0, self.padding),
            )
            self._create_hints_label(hints_frame)

    def _create_hints_label(self, hints_frame):
        hints_label = ttk.Label(
            hints_frame,
            text=translate("merge_screen_conflicts_hints"),
            style="Hints.TLabel",
        )
        hints_label.grid(row=0, column=0, columnspan=2, sticky="ew")

    def _process_selected_files(self):
        merging_engine = settings.MERGING_ENGINE
        tool_paths = settings.TOOLS_PATHS
        if merging_engine == "WinMerge":
            engine_path = Path(tool_paths.get("winmerge"))
        elif merging_engine == "kdiff3":
            engine_path = Path(tool_paths.get("kdiff3"))
        if not engine_path.exists():
            messagebox.showerror(
                translate("generic_error"),
                f'{merging_engine} {translate("merge_screen_conflicts_no_merging_engine_1")} {str(engine_path)}\n{translate("merge_screen_conflicts_no_merging_engine_2")}',
                parent=self.window,
            )
            return

        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("merge_screen_conflicts_select_files"),
                parent=self.window,
            )
            return

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
                    log.debug(f"{item_name} sourcs paths: {item_sources_paths}...")

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
                    log.error(f"Missing key for item '{item_name}': {e}")
                    self.not_processed.append(f"{item_name} (missing key)")
                except Exception as e:
                    log.error(f"Error processing '{item_name}': {e}")
                    self.not_processed.append(f"{item_name} (processing error)")

            if not self.processed_conflicts and self.not_processed:
                not_processed_str = "\n".join(map(str, self.not_processed))
                not_processed_str2 = ", ".join(map(str, self.not_processed))
                log.warning("No files were processed!")
                log.debug(f"Skipped files: {not_processed_str2}")
                messagebox.showinfo(
                    translate("generic_warning"),
                    f'{translate("merge_screen_conflicts_no_files_processed")}\n\n{translate("merge_screen_conflicts_final_report_3")}\n{not_processed_str}',
                    parent=self.window,
                )
                return
            elif Files.is_folder_empty(temp_merging_dir):
                messagebox.showerror(
                    translate("generic_error"),
                    translate("merge_dir_is_empty"),
                    parent=self.window,
                )
                return
            else:
                folder_to_place_merged_mod = self._insistent_askdirectory()
                if folder_to_place_merged_mod:

                    formatted_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    merged_mod_path = (
                        folder_to_place_merged_mod / f"z_zonepaq_merged_{formatted_time}_P.pak"
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
                            messagebox.showinfo(
                                translate("generic_success"),
                                f'{translate("merge_screen_conflicts_final_report_1")}\n{repak_result}\n\n'
                                f'{translate("merge_screen_conflicts_final_report_2")}\n{processed_str or translate("generic_none")}\n\n'
                                f'{translate("merge_screen_conflicts_final_report_3")}\n{not_processed_str or translate("generic_none")}',
                                parent=self.window,
                            )
                        else:
                            messagebox.showerror(
                                translate("generic_error"),
                                f'{translate("merge_screen_conflicts_repak_error")} {repak_result}',
                                parent=self.window,
                            )

                    except Exception as e:
                        messagebox.showerror(
                            translate("generic_error"),
                            f'{translate("merge_screen_conflicts_repak_error")} {str(e)}',
                            parent=self.window,
                        )
                        log.error(f"Unexpected error during repack: {str(e)}")

                else:
                    messagebox.showwarning(
                        translate("generic_warning"),
                        translate("merge_screen_conflicts_aborted"),
                        parent=self.window,
                    )

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
            unpacked_files = self._unpack_files(
                item_sources_paths, item_sources_names, item_path, temp_dir_path
            )
            self._merge_files(
                unpacked_files,
                item_name,
                item_path,
                temp_merging_dir,
                use_vanilla,
            )

    def _unpack_files(
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
                    if unpacked_file.exists():
                        unpacked_files.append(unpacked_file)
                    else:
                        log.warning(f"Unpacked file does not exist: {unpacked_file}")
                else:
                    log.error(f"Unpack failed for {item_source_path}")
            except FileNotFoundError as e:
                log.error(
                    f"File not found: {item_sources_names[i]} -> {item_source_path}: {e}"
                )
            except Exception as e:
                log.error(f"Unexpected error unpacking {item_sources_names[i]}: {e}")

        return unpacked_files

    def _merge_files(
        self, unpacked_files, item_name, item_path, temp_merging_dir, use_vanilla=False
    ):
        if unpacked_files:
            save_path = temp_merging_dir / item_path
            save_path.parent.mkdir(parents=True, exist_ok=True)

            if use_vanilla:
                vanilla_file = (
                    Path(settings.GAME_PATHS.get("vanilla_unpacked")) / item_path
                )
                if vanilla_file.exists():
                    unpacked_files.appendleft(vanilla_file)

            compare_success, compare_result = Merging._run_engine(
                unpacked_files, save_path
            )
            log.debug(f"{settings.MERGING_ENGINE} returned with code {compare_result.returncode}")

            if compare_success and compare_result.returncode == 0:
                log.info(f"Merging successful for {str(item_path)}")
                self.processed_conflicts.append(item_name)
            else:
                log.error(
                    f"Merging failed for {str(item_path)}: {compare_result.stderr}"
                )
                self.not_processed.append(
                    f"{item_name} (wasn't saved in {settings.MERGING_ENGINE})"
                )
        else:
            log.error(f"No valid files to compare for {str(item_path)}")

    def _insistent_askdirectory(self, initialdir=None, title=None):
        folder_selected = None
        while True:
            folder_selected = filedialog.askdirectory(
                initialdir=initialdir, title=title
            )

            if folder_selected:
                return Path(folder_selected)
            else:
                retry = messagebox.askyesno(
                    translate("generic_warning"),
                    translate("merge_screen_conflicts_select_merged_destination"),
                    parent=self.window,
                )
                if not retry:
                    return None

    def _populate_tree(self, parent_node, data):
        queue = deque([(parent_node, data, [])])

        no_conflicts_count = 0
        dual_match_count = 0
        dual_no_match_count = 0
        tri_count = 0
        complex_count = 0

        while queue:
            current_parent_node, current_data, parent_path = queue.popleft()

            sorted_items = sorted(
                current_data.items(),
                key=lambda item: (not isinstance(item[1], dict), item[0].lower()),
            )

            for key, value in sorted_items:
                full_path = str(Path(*parent_path) / key)

                if isinstance(value, list):
                    num_sources = len(value)
                    has_match = self._has_vanilla_match(full_path)

                    tag = self._determine_tag(num_sources, has_match)
                    if tag:
                        if tag == "no_conflicts":
                            no_conflicts_count += 1
                        elif tag == "dual_match":
                            dual_match_count += 1
                        elif tag == "dual_no_match":
                            dual_no_match_count += 1
                        elif tag == "tri":
                            tri_count += 1
                        elif tag == "complex":
                            complex_count += 1

                    self._insert_node_into_tree(
                        current_parent_node, key, value, full_path, tag
                    )

                elif isinstance(value, dict):
                    node = self.tree.insert(
                        current_parent_node,
                        "end",
                        text=key,
                        values=["", "", ""],  # Empty values for nested directories
                    )
                    queue.append((node, value, parent_path + [key]))

                else:
                    self._insert_node_into_tree(
                        current_parent_node, key, value, "", None
                    )

                self.tree.item(node, open=True)

        return {
            "no_conflicts_count": no_conflicts_count,
            "dual_match_count": dual_match_count,
            "dual_no_match_count": dual_no_match_count,
            "tri_count": tri_count,
            "complex_count": complex_count,
        }

    def _insert_node_into_tree(self, parent_node, key, value, full_path, tag):
        sorted_value = sorted(value, key=lambda src: Path(src).name)

        source_paths = [str(Path(src)) for src in sorted_value]
        source_filenames = [str(Path(src).name) for src in sorted_value]

        self.tree.insert(
            parent_node,
            "end",
            text=key,
            values=[", ".join(source_filenames), ", ".join(source_paths), full_path],
            tags=[tag] if tag else [],
        )

    def _determine_tag(self, num_sources, has_match):
        if num_sources == 1:
            return "no_conflicts"
        if num_sources == 2:
            return "dual_match" if has_match else "dual_no_match"
        elif num_sources == 3:
            return "tri"
        elif num_sources > 3:
            return "complex"
        return None

    def _search_tree(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        filtered_data = (
            self._filter_data(self.original_data, query)
            if query
            else self.original_data
        )

        self._populate_tree("", filtered_data)

    def _filter_data(self, data, query):
        filtered = {}
        for key, value in data.items():
            if isinstance(value, dict):
                nested_filtered = self._filter_data(value, query)
                if nested_filtered:
                    filtered[key] = nested_filtered
            elif isinstance(value, list):
                if query in key.lower() or any(query in str(v).lower() for v in value):
                    filtered[key] = value
            elif query in key.lower() or query in str(value).lower():
                filtered[key] = value
        return filtered

    def _toggle_path_display(self):
        if self.show_full_paths.get():
            self.tree.column("PAK Sources", width=0, stretch=tk.NO)
            self.tree.column("PAK Sources Paths", stretch=True)
        else:
            self.tree.column("PAK Sources", stretch=True)
            self.tree.column("PAK Sources Paths", width=0, stretch=tk.NO)

    def _has_vanilla_match(self, conflict):
        return (Path(settings.GAME_PATHS.get("vanilla_unpacked")) / conflict).exists()
