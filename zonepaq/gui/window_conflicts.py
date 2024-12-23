import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import messagebox, ttk

from backend.conflicts import ConflictProcessor
from backend.logger import log
from config.settings import SettingsManager
from config.translations import translate
from gui.template_toplevel import WindowTemplateToplevel

# Get SettingsManager class
settings = SettingsManager()


class WindowConflicts(WindowTemplateToplevel):
    """Displays conflict reports and provides tools to analyze and merge files."""

    def __init__(self, master, content_tree):
        super().__init__(
            master=master,
            title=translate("merge_screen_conflicts_title"),
        )
        self.content_tree = content_tree
        self.original_data = content_tree
        # self.theme_dict = settings.THEME_DICT  # !fixme

        # Variable for checkbutton state
        self.show_full_paths = tk.BooleanVar(value=False)

        self.setup()

        self.adjust_to_content(self, adjust_width=True, adjust_height=False)

        log.info("Conflicts resolver window opened.")

    def on_closing(self):
        log.debug("Conflicts resolver window closed.")
        self.destroy()
        self.master.deiconify()

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
        self.search_var = tk.StringVar(master=self)
        self.search_var.trace_add("write", lambda *args: self._search_tree())
        # self.search_entry = CustomEntry(
        #     parent=search_frame,
        #     customization_manager=self.root.customization_manager,
        #     textvariable=self.search_var,
        #     style="PathEntry.TEntry",
        #     window=self.window,
        # )
        # self.search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5), pady=5)

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
            selectmode="extended",
        )
        self._configure_treeview_headings()
        self._configure_treeview_columns()

        # Treeview Tag Configuration
        # self.tree.tag_configure(
        #     "no_conflicts", foreground=self.theme_dict["color_success"]  # !fixme
        # )
        # self.tree.tag_configure(
        #     "dual_match", foreground=self.theme_dict["color_foreground"]  # !fixme
        # )
        # self.tree.tag_configure(
        #     "dual_no_match", foreground=self.theme_dict["color_attention"]  # !fixme
        # )
        # self.tree.tag_configure("tri", foreground=self.theme_dict["color_warning"])  # !fixme
        # self.tree.tag_configure("complex", foreground=self.theme_dict["color_error"])  # !fixme

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

        # select_all_button = CustomButton(
        #     parent=buttons_frame,
        #     customization_manager=self.root.customization_manager,
        #     text=translate("merge_screen_conflicts_select_all_button"),
        #     command=lambda: self._select_tagged_items(),
        #     style="TButton",
        #     width=160,
        #     height=55,
        #     window=self.window,
        # )
        # select_all_button.grid(
        #     row=0,
        #     column=0,
        #     padx=(0, self.padding),
        #     sticky="ne",
        # )

        # process_button = CustomButton(
        #     parent=buttons_frame,
        #     customization_manager=self.root.customization_manager,
        #     text=translate("merge_screen_conflicts_action_button"),
        #     command=lambda: self._process_selected_files(),
        #     style="Accent.TButton",
        #     width=160,
        #     height=55,
        #     window=self.window,
        # )
        # process_button.grid(row=0, column=1, sticky="ne")

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
        processor = ConflictProcessor(self.tree, self.ignore_no_conflicts)
        messagebox_type, messagebox_message = processor.process_selected_files()
        messagebox_functions = {
            "info": messagebox.showinfo,
            "warning": messagebox.showwarning,
            "error": messagebox.showerror,
        }

        if messagebox_type in messagebox_functions:
            messagebox_functions[messagebox_type](
                translate(f"generic_{messagebox_type}"),
                messagebox_message,
                parent=self.window,
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
        vanilla_path = Path(settings.GAME_PATHS.get("vanilla_unpacked")) / conflict
        return vanilla_path.exists() and vanilla_path.is_file()
