from collections import deque
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from backend.conflicts import ConflictProcessor
from backend.logger import log
from config.settings_manager import settings
from config.translations import translate
from gui.template_toplevel import TemplateToplevel
from gui.window_messagebox import WindowMessageBox


class WindowConflicts(TemplateToplevel):
    """Displays conflict reports and provides tools to analyze and merge files."""

    def __init__(self, master, content_tree):
        super().__init__(
            master=master,
            title=translate("merge_screen_conflicts_title"),
        )

        self.content_tree = content_tree
        self.original_data = content_tree

        # Variable for checkbutton state
        self.show_full_paths = ctk.BooleanVar(value=False)

        self.setup()

        self.adjust_to_content(self, adjust_width=True, adjust_height=True)

        log.info("Conflicts resolver window opened.")

    def on_closing(self):
        log.info("Conflicts resolver window closed.")
        self.destroy()
        # self.master.deiconify()

    def setup(self):
        self._create_search_frame()
        self._create_tree_frame()
        self._create_legend_frame()
        self._create_hints_frame()

    def _create_search_frame(self):
        search_frame = self.create_frame(
            self, row=0, column=0, columnspan=2, sticky="ew", column_weights=[(1, 1)]
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_search_label(search_frame)
        self._create_search_entry(search_frame)
        self._create_show_paths_check_button(search_frame)

    def _create_search_label(self, search_frame):
        search_label = self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": search_frame,
                "text": translate("generic_search"),
                "justify": "left",
                "anchor": "w",
            },
            grid_args={
                "row": 0,
                "column": 0,
                "sticky": "w",
                "padx": (self.padding / 2, self.padding / 4),
                "pady": self.padding / 4,
            },
        )

    def _create_search_entry(self, search_frame):
        self.search_var = ctk.StringVar(master=self)
        self.search_var.trace_add("write", lambda *args: self._search_tree())
        self.search_entry = self.create_ctk_widget(
            ctk_widget=ctk.CTkEntry,
            widget_args={
                "master": search_frame,
                "textvariable": self.search_var,
            },
            grid_args={
                "row": 0,
                "column": 1,
                "sticky": "ew",
                "padx": self.padding / 4,
                "pady": self.padding / 4,
            },
        )

    def _create_show_paths_check_button(self, search_frame):
        self.show_paths_check_button = self.create_ctk_widget(
            ctk_widget=ctk.CTkCheckBox,
            widget_args={
                "master": search_frame,
                "text": translate("merge_screen_conflicts_show_path"),
                "variable": self.show_full_paths,
                "command": self._toggle_path_display,
            },
            grid_args={
                "row": 0,
                "column": 2,
                "padx": self.padding / 4,
            },
        )

    def _create_tree_frame(self):
        tree_frame = self.create_frame(
            self,
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            # padx=self.padding,
            # pady=self.padding,
            row_weights=[(0, 1)],
            column_weights=[(0, 1)],
        )

        self._create_treeview(tree_frame)
        self._create_scrollbar(tree_frame)

    def _create_treeview(self, tree_frame):

        bg_color = self._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        text_color = self.theme_manager.get_color_for_mode(
            "color_text_muted", settings.THEME_NAME
        )
        selected_color = self.theme_manager.get_color_for_mode(
            "color_highlight", settings.THEME_NAME
        )

        treestyle = ttk.Style()
        treestyle.theme_use("default")
        treestyle.configure(
            "Treeview",
            background=bg_color,
            foreground=text_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=("Consolas", 10, "normal"),
        )
        treestyle.map(
            "Treeview",
            background=[("selected", bg_color)],
            foreground=[("selected", selected_color)],
        )
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("PAK Sources", "PAK Sources Paths", "File Path"),
            show="tree headings",
            height=15,
            selectmode="extended",
        )

        self._configure_treeview_headings()
        self._configure_treeview_columns()

        # Treeview Tag Configuration
        self.tree.tag_configure(
            "no_conflicts",
            foreground=self.theme_manager.get_color_for_mode(
                "color_success", settings.THEME_NAME
            ),
        )
        self.tree.tag_configure(
            "dual_match",
            foreground=self.theme_manager.get_color_for_mode(
                "color_text_primary", settings.THEME_NAME
            ),
        )
        self.tree.tag_configure(
            "dual_no_match",
            foreground=self.theme_manager.get_color_for_mode(
                "color_attention", settings.THEME_NAME
            ),
        )
        self.tree.tag_configure(
            "tri",
            foreground=self.theme_manager.get_color_for_mode(
                "color_warning", settings.THEME_NAME
            ),
        )
        self.tree.tag_configure(
            "complex",
            foreground=self.theme_manager.get_color_for_mode(
                "color_error", settings.THEME_NAME
            ),
        )

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
        self.tree.column("#0", width=400, stretch=False)
        self.tree.column("PAK Sources", stretch=True)
        self.tree.column(
            "PAK Sources Paths", width=0, stretch=False
        )  # Invisible column
        self.tree.column("File Path", width=0, stretch=False)  # Invisible column

    def _create_scrollbar(self, tree_frame):
        self.scrollbar_v = self.create_ctk_widget(
            ctk_widget=ctk.CTkScrollbar,
            widget_args={
                "master": tree_frame,
                "orientation": "vertical",
                "command": self.tree.yview,
            },
            grid_args={
                "row": 0,
                "column": 1,
                "sticky": "ns",
            },
        )
        self.tree.configure(yscrollcommand=self.scrollbar_v.set)

        # ! fixme
        # self.scrollbar_h = self.create_ctk_widget(
        #     ctk_widget=ctk.CTkScrollbar,
        #     widget_args={
        #         "master": tree_frame,
        #         "orientation": "horizontal",
        #         "command": self.tree.xview,
        #     },
        #     grid_args={
        #         "row": 1,
        #         "column": 0,
        #         "sticky": "ew",
        #     },
        # )
        # self.tree.configure(xscrollcommand=self.scrollbar_h.set)

        self.tree.grid(row=0, column=0, sticky="nsew")

    def _create_legend_frame(self):
        legend_frame = self.create_frame(
            self,
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=self.padding,
            pady=self.padding,
            column_weights=[(0, 1), (1, 0)],
        )

        self._create_legend_labels(legend_frame)
        self._create_process_frame(legend_frame)

    def _create_legend_labels(self, legend_frame):
        label_no_conflicts_count = self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_no_conflicts_count')} {self.conflict_counts['no_conflicts_count']}",
            style="Success.CTkLabel",
            row=1,
        )
        self.add_tooltip(
            label_no_conflicts_count,
            translate("tooltip_button_label_no_conflicts_count"),
        )

        label_dual_match_count = self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_dual_match_count')} {self.conflict_counts['dual_match_count']}",
            style="Normal.CTkLabel",
            row=2,
        )
        self.add_tooltip(
            label_dual_match_count, translate("tooltip_button_label_dual_match_count")
        )

        label_dual_no_match_count = self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_dual_no_match_count')} {self.conflict_counts['dual_no_match_count']}",
            style="Attention.CTkLabel",
            row=3,
        )
        self.add_tooltip(
            label_dual_no_match_count,
            translate("tooltip_button_label_dual_no_match_count"),
        )

        label_tri_count = self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_tri_count')} {self.conflict_counts['tri_count']}",
            style="Warning.CTkLabel",
            row=4,
        )
        self.add_tooltip(label_tri_count, translate("tooltip_button_label_tri_count"))

        label_complex_count = self._create_legend_label(
            legend_frame,
            text=f"{translate('merge_screen_conflicts_complex_count')} {self.conflict_counts['complex_count']}",
            style="Error.CTkLabel",
            row=5,
        )
        self.add_tooltip(
            label_complex_count, translate("tooltip_button_label_complex_count")
        )

    def _create_legend_label(self, legend_frame, text, style, row):
        return self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": legend_frame,
                "text": text,
                "justify": "left",
                "anchor": "w",
            },
            widget_style=style,
            grid_args={
                "row": row,
                "column": 0,
                "sticky": "ew",
            },
        )

    def _create_process_frame(self, legend_frame):
        process_frame = self.create_frame(
            legend_frame,
            row=1,
            column=1,
            rowspan=4,
            padx=(self.padding * 2, 0),
            sticky="ne",
        )

        self.ignore_no_conflicts = True
        self.ignore_no_conflicts_var = ctk.BooleanVar(value=self.ignore_no_conflicts)

        self.ignore_no_conflicts_check_button = self.create_ctk_widget(
            ctk_widget=ctk.CTkCheckBox,
            widget_args={
                "master": process_frame,
                "text": translate("merge_screen_ignore_no_conflicts_checkbutton"),
                "variable": self.ignore_no_conflicts_var,
                "command": self._toggle_ignore_no_conflicts,
            },
            grid_args={
                "row": 0,
                "column": 0,
                "pady": (0, self.padding / 2),
                "sticky": "ne",
            },
        )
        self.add_tooltip(
            self.ignore_no_conflicts_check_button,
            translate("tooltip_checkbox_ignore_no_conflicts"),
        )

        buttons_frame = self.create_frame(
            process_frame,
            row=1,
            column=0,
            sticky="ne",
        )

        button_select_all = self.create_button(
            buttons_frame,
            text=translate("merge_screen_conflicts_select_all_button"),
            command=lambda: self._select_tagged_items(),
            width=150,
            height=40,
            row=0,
            column=0,
            padx=(0, self.padding),
            sticky="ne",
        )
        self.add_tooltip(
            button_select_all,
            translate("tooltip_button_select_all"),
        )

        button_process = self.create_button(
            buttons_frame,
            text=translate("merge_screen_conflicts_action_button"),
            command=lambda: self._process_selected_files(),
            style="Action.CTkButton",
            width=150,
            height=40,
            row=0,
            column=1,
            sticky="ne",
        )
        self.add_tooltip(
            button_process,
            translate("tooltip_button_process"),
        )

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
            hints_frame = self.create_frame(
                self,
                row=3,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=self.padding,
                pady=(0, self.padding),
            )

            self._create_hints_label(hints_frame)

    def _create_hints_label(self, hints_frame):
        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": hints_frame,
                "text": translate("merge_screen_conflicts_hints"),
                "justify": "left",
                "anchor": "w",
            },
            widget_style="Hints.CTkLabel",
            grid_args={
                "row": 0,
                "column": 0,
                "columnspan": 2,
                "sticky": "ew",
            },
        )

    def _process_selected_files(self):
        processor = ConflictProcessor(self, self.ignore_no_conflicts)
        messagebox_type, messagebox_message = processor.process_selected_files()
        messagebox_functions = {
            "info": WindowMessageBox.showinfo,
            "warning": WindowMessageBox.showwarning,
            "error": WindowMessageBox.showerror,
        }

        if messagebox_type in messagebox_functions:
            messagebox_functions[messagebox_type](
                self,
                message=messagebox_message,
            )

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

                    self.tree.item(node, open=True)

                else:
                    self._insert_node_into_tree(
                        current_parent_node, key, value, "", None
                    )

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
            self.tree.column("PAK Sources", width=0, stretch=ctk.NO)
            self.tree.column("PAK Sources Paths", stretch=True)
        else:
            self.tree.column("PAK Sources", stretch=True)
            self.tree.column("PAK Sources Paths", width=0, stretch=ctk.NO)

    def _has_vanilla_match(self, conflict):
        for vanilla_file in self.games_manager.vanilla_files:
            unpacked = vanilla_file["unpacked"]
            vanilla_path = Path(unpacked) / conflict
            if vanilla_path.exists() and vanilla_path.is_file():
                return True
        return False
