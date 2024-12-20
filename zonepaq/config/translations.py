TRANSLATIONS = {
    "English": {
        "meta_description": "A user-friendly GUI application for unpacking, repacking, and solving .pak mods conflicts.",
        "meta_developer": "Developer:",
        "menu_file": "File",
        "menu_file_exit": "Exit",
        "menu_preferences": "Preferences",
        "menu_preferences_settings": "Settings",
        "menu_help": "Help",
        "menu_help_license": "View License",
        "menu_help_homepage": "Visit Homepage",
        "menu_help_about": "About",
        "settings_general": "General",
        "settings_general_path_tools": "Executables Paths",
        "settings_general_path_game": "Game Paths",
        "settings_general_vanilla_unpacked": "Vanilla Unpacked",
        "settings_general_keys": "Encryption Keys",
        "settings_general_aes_key": "AES Key",
        "settings_general_merging_engine": "Merging Engine",
        "settings_general_used_tool": "Used Tool",
        "settings_general_browse": "Browse",
        "settings_general_install": "Install",
        "settings_general_unpack": "Unpack",
        "settings_general_get": "Get",
        "settings_appearance": "Appearance",
        "settings_appearance_customization": "Customization",
        "settings_appearance_color_theme": "Color Theme",
        "settings_appearance_dark_mode": "Dark Mode",
        "settings_appearance_localization": "Localization",
        "settings_appearance_language": "Language",
        "settings_appearance_onboarding": "Onboarding",
        "settings_appearance_hints": "Hints",
        "settings_appearance_show_hints": "Show Hints in GUI",
        "settings_require_restart": "* Require a restart for changes to take effect",
        "settings_save": "Save",
        "generic_question": "Question",
        "generic_info": "Success",
        "generic_warning": "Warning",
        "generic_error": "Error!",
        "generic_results": "Results",
        "generic_search": "Search:",
        "generic_process": "Process",
        "generic_none": "None",
        "generic_dnd": "Drag and drop",
        "generic_here": "here",
        "pak": ".pak files",
        "folders": "folders",
        "launch_screen_title": "Welcome",
        "launch_screen_header": "What would you like to do?",
        "launch_screen_button_repak": "Unpack or repack",
        "launch_screen_button_merge": "Find conflicts or merge",
        "repak_screen_title": "Unpack and Repack .pak Files",
        "repak_screen_unpack_header": "Unpack .pak files",
        "repak_screen_unpack_hints": (
            "Instructions:\n"
            "1. Add one or more .pak files using one of the following methods:\n"
            '  - Clicking the "Add" button.\n'
            "  - Copying them from Explorer and pressing CTRL+V while the list box is selected.\n"
            '2. Click the "Unpack" button and choose a destination folder\n'
            "...each .pak file will be unpacked into a separate folder at the selected destination..."
        ),
        "repak_screen_unpack_button": "Unpack all",
        "repak_screen_unpack_msg_empty_list": "Please, select some files to unpack.",
        "repak_screen_unpack_msg_overwrite_1": "The following folders already exist:",
        "repak_screen_unpack_msg_overwrite_2": "Do you want to overwrite them all?",
        "repak_screen_repack_header": "Repack folders",
        "repak_screen_repack_hints": (
            "Instructions:\n"
            "1. Add one or more folders using one of the following methods:\n"
            '  - Clicking the "Add" button.\n'
            "  - Copying them from Explorer and pressing CTRL+V while the list box is selected.\n"
            '2. Click the "Repack" button and choose a destination folder\n'
            "...each folder will be repacked into a separate .pak file at the selected destination..."
        ),
        "repak_screen_repack_button": "Repack all",
        "repak_screen_repack_msg_empty_list": "Please, select some folders to repack.",
        "button_add": "Add",
        "button_remove": "Remove",
        "button_clear": "Clear",
        "merge_screen_title": "Find conflicts or merge mods",
        "merge_screen_header": "Resolve conflicts between mods",
        "merge_screen_hints": (
            "Instructions:\n"
            "1. Add one or more .pak files using one of the following methods:\n"
            '  - Clicking the "Add" button.\n'
            "  - Copying them from Explorer and pressing CTRL+V while the list box is selected.\n"
            '2. Click the "Analyze" button.\n'
            "...the merging window will open..."
        ),
        "merge_screen_analyze_button": "Analyze all",
        "merge_screen_conflicts_title": "Find conflicts or merge mods",
        "merge_screen_conflicts_show_path": "Show full path",
        "merge_screen_conflicts_file_structure": "File Tree",
        "merge_screen_conflicts_pak_sources": "PAK Sources",
        "merge_screen_conflicts_pak_sources_paths": "PAK Sources Paths",
        "merge_screen_conflicts_no_conflicts_count": "Number of files without conflicts:",
        "merge_screen_conflicts_dual_match_count": "Number of dual-source conflicts with matching vanilla files:",
        "merge_screen_conflicts_dual_no_match_count": "Number of dual-source conflicts without matching vanilla files:",
        "merge_screen_conflicts_tri_count": "Number of tri-source conflicts:",
        "merge_screen_conflicts_complex_count": "Number of complex conflicts:",
        "merge_screen_conflicts_select_files": "Please, select files in the tree view to continue.",
        "merge_screen_conflicts_no_files_processed": "No files were processed!",
        "merge_screen_conflicts_final_report_1": "Merged mod was saved at:",
        "merge_screen_conflicts_final_report_2": "Processed:",
        "merge_screen_conflicts_final_report_3": "Skipped:",
        "error_executable_not_found_1": "wasn't found at:",
        "error_executable_not_found_2": 'Please, enter correct path to an executable file (".exe") in the settings and try again.',
        "merge_screen_conflicts_repak_error": "Merged mod wasn't saved with repak error:",
        "merge_screen_conflicts_aborted": "Merged mod wasn't saved: aborted by user.",
        "merge_dir_is_empty": "The folder for merging is empty!\nPlease make sure to save the merged file before closing the merging engine.",
        "merge_screen_conflicts_select_merged_destination": "No folder was selected. Would you like to try again?",
        "merge_screen_ignore_no_conflicts_checkbutton": "Ignore files without conflicts",
        "merge_screen_conflicts_action_button": "Process",
        "merge_screen_conflicts_select_all_button": "Select All",
        "merge_screen_conflicts_hints": (
            "Instructions:\n"
            '1. Select multiple conflicting files in the tree view by holding CTRL or SHIFT and clicking on them, then click the "Process" button.\n'
            "...the source .pak files for each conflict will be unpacked, and the conflicting files will be opened in the merging engine in groups...\n"
            "2. Resolve each conflict manually or use auto-merge, then save the resulting file. Important: don't change suggested save location!\n"
            "...once all conflicts are resolved and the last merging engine window is closed, saved files will be repacked into a merged mod at the location of your choice...\n"
            "\n"
            "Please, note:\n"
            "- You have to unpack vanilla files and set their location in the settings menu if you plan to use them in comparisons;\n"
            '- Files without conflicts will be included in the merged mod only if "Ignore files without conflicts" is unchecked;\n'
            "- Dual-source conflicts will be opened in the merging engine with a matching vanilla file as a base for merging;\n"
            "- Tri-source conflicts will be opened in the merging engine without vanilla base;\n"
            "- Complex conflicts can't be processed due to the limitation of 3 files open at a time in the merging engine."
        ),
        "dialogue_pak_files": "PAK files",
        "dialogue_tools_redowndload_installer": (
            "installer exists.\n" "Do you want to redownload the latest version?"
        ),
        "dialogue_tools_reinstall": ("exists.\n" "Do you want to reinstall it?"),
    },
    "Русский": {
        "meta_description": "Удобное графическое приложение для распаковки, упаковки и разрешения конфликтов .pak модов.",
        "meta_developer": "Разработчик:",
        "menu_file": "Файл",
        "menu_file_exit": "Выход",
        "menu_preferences": "Параметры",
        "menu_preferences_settings": "Настройки",
        "menu_help": "Справка",
        "menu_help_license": "Просмотреть лицензию",
        "menu_help_homepage": "Посетить домашнюю страницу",
        "menu_help_about": "О программе",
        "settings_general": "Общие",
        "settings_general_path_tools": "Пути к исполняемым файлам",
        "settings_general_path_game": "Пути к игровым папкам",
        "settings_general_vanilla_unpacked": "Оригинальные файлы",
        "settings_general_keys": "Ключи шифрования",
        "settings_general_aes_key": "Ключ AES",
        "settings_general_merging_engine": "Утилита сравнения",
        "settings_general_used_tool": "Утилита",
        "settings_general_browse": "Обзор",
        "settings_general_install": "Установить",
        "settings_general_unpack": "Распаковать",
        "settings_general_get": "Получить",
        "settings_appearance": "Внешний вид",
        "settings_appearance_customization": "Кастомизация",
        "settings_appearance_color_theme": "Цветовая тема",
        "settings_appearance_dark_mode": "Тёмный режим",
        "settings_appearance_localization": "Локализация",
        "settings_appearance_language": "Язык",
        "settings_appearance_onboarding": "Адаптация",
        "settings_appearance_hints": "Подсказки",
        "settings_appearance_show_hints": "Показывать подсказки в интерфейсе",
        "settings_require_restart": "* Требуется перезапуск для применения изменений",
        "settings_save": "Сохранить",
        "generic_question": "Вопрос",
        "generic_info": "Успех",
        "generic_warning": "Предупреждение",
        "generic_error": "Ошибка!",
        "generic_results": "Результаты",
        "generic_search": "Поиск:",
        "generic_process": "Обработать",
        "generic_none": "Ни одного",
        "generic_dnd": "Перетащите",
        "generic_here": "сюда",
        "pak": ".pak файлы",
        "folders": "папки",
        "launch_screen_title": "Добро пожаловать",
        "launch_screen_header": "Что вы хотите сделать?",
        "launch_screen_button_repak": "Распаковать или упаковать",
        "launch_screen_button_merge": "Найти конфликты или объединить",
        "repak_screen_title": "Распаковка и упаковка .pak файлов",
        "repak_screen_unpack_header": "Распаковать .pak файлы",
        "repak_screen_unpack_hints": (
            "Инструкция:\n"
            "1. Добавьте один или несколько .pak файлов одним из следующих способов:\n"
            '  - Нажмите кнопку "Добавить".\n'
            "  - Скопируйте их из проводника и нажмите CTRL+V, когда выделен список.\n"
            '2. Нажмите кнопку "Распаковать" и выберите папку назначения.\n'
            "...каждый .pak файл будет распакован в отдельную папку по выбранному пути..."
        ),
        "repak_screen_unpack_button": "Распаковать все",
        "repak_screen_unpack_msg_empty_list": "Пожалуйста, выберите файлы для распаковки.",
        "repak_screen_unpack_msg_overwrite_1": "Следующие папки уже существуют:",
        "repak_screen_unpack_msg_overwrite_2": "Хотите их перезаписать?",
        "repak_screen_repack_header": "Упаковать папки",
        "repak_screen_repack_hints": (
            "Инструкция:\n"
            "1. Добавьте одну или несколько папок одним из следующих способов:\n"
            '  - Нажмите кнопку "Добавить".\n'
            "  - Скопируйте их из проводника и нажмите CTRL+V, когда выделен список.\n"
            '2. Нажмите кнопку "Упаковать" и выберите папку назначения.\n'
            "...каждая папка будет упакована в отдельный .pak файл по выбранному пути..."
        ),
        "repak_screen_repack_button": "Упаковать все",
        "repak_screen_repack_msg_empty_list": "Пожалуйста, выберите папки для упаковки.",
        "button_add": "Добавить",
        "button_remove": "Убрать",
        "button_clear": "Очистить",
        "merge_screen_title": "Поиск конфликтов или слияние модов",
        "merge_screen_header": "Разрешение конфликтов между модами",
        "merge_screen_hints": (
            "Инструкция:\n"
            "1. Добавьте один или несколько .pak файлов одним из следующих способов:\n"
            '  - Нажмите кнопку "Добавить".\n'
            "  - Скопируйте их из проводника и нажмите CTRL+V, когда выделен список.\n"
            '2. Нажмите кнопку "Анализировать".\n'
            "...откроется окно слияния..."
        ),
        "merge_screen_analyze_button": "Анализировать все",
        "merge_screen_conflicts_title": "Поиск конфликтов или слияние модов",
        "merge_screen_conflicts_show_path": "Показать полный путь",
        "merge_screen_conflicts_file_structure": "Дерево файлов",
        "merge_screen_conflicts_pak_sources": "Источник PAK",
        "merge_screen_conflicts_pak_sources_paths": "Пути источников PAK",
        "merge_screen_conflicts_no_conflicts_count": "Количество файлов без конфликтов:",
        "merge_screen_conflicts_dual_match_count": "Количество конфликтов с двумя источниками и найденным оригинальным файлом:",
        "merge_screen_conflicts_dual_no_match_count": "Количество конфликтов с двумя источниками без найденного оригинального файла:",
        "merge_screen_conflicts_tri_count": "Количество конфликтов с тремя источниками:",
        "merge_screen_conflicts_complex_count": "Количество сложных конфликтов:",
        "merge_screen_conflicts_select_files": "Пожалуйста, выберите файлы в дереве для продолжения.",
        "merge_screen_conflicts_final_report_1": "Объединенный мод сохранён в:",
        "merge_screen_conflicts_final_report_2": "Обработано:",
        "merge_screen_conflicts_final_report_3": "Пропущено:",
        "error_executable_not_found_1": "не найден по пути:",
        "error_executable_not_found_2": 'Пожалуйста, введите правильный путь к исполняемому файлу (".exe") в настройках и попробуйте заново.',
        "merge_screen_conflicts_repak_error": "Объединённый мод не был сохранён из-за ошибки упаковки:",
        "merge_screen_conflicts_aborted": "Объединение отменено пользователем.",
        "merge_dir_is_empty": "Папка для упаковки пуста!\nПожалуйста, убедитесь, что вы сохранили объединённый файл перед закрытием утилиты сравнения.",
        "merge_screen_conflicts_select_merged_destination": "Папка не выбрана. Попробовать снова?",
        "merge_screen_ignore_no_conflicts_checkbutton": "Игнорировать файлы без конфликтов",
        "merge_screen_conflicts_action_button": "Обработать",
        "merge_screen_conflicts_select_all_button": "Выбрать все",
        "merge_screen_conflicts_hints": (
            "Инструкция:\n"
            '1. Выберите несколько конфликтующих файлов в дереве, удерживая CTRL или SHIFT и нажимая на них, затем нажмите кнопку "Обработать".\n'
            "...исходные .pak файлы для каждого конфликта будут распакованы, а конфликтующие файлы будут открываться в утилите сравнения по группам...\n"
            "2. Разрешите каждый конфликт вручную или используйте авто-слияние, затем сохраните результат. Важно: не меняйте предложенный путь сохранения!\n"
            "...когда все конфликты будут разрешены и последнее окно утилиты сравнения будет закрыто, сохраненные файлы будут упакованы в объединенный мод по выбранному пути...\n"
            "\n"
            "Пожалуйста, учтите:\n"
            "- Чтобы использовать оригинальные файлы в сравнении, они должны быть пердварительно распакованы и указаны в настройках путей;\n"
            '- Файлы без конфликтов будут включены в объединённый мод только если флажок "Игнорировать файлы без конфликтов" снят;\n'
            "- Конфликты с двумя источниками откроются в утилите сравнения с оригинальным файлом в качестве основы;\n"
            "- Конфликты с тремя источниками откроются в утилите сравнения без оригинальной основы;\n"
            "- Сложные конфликты не могут быть обработаны из-за ограничения в утилите сравнения на открытие 3 файлов одновременно."
        ),
        "dialogue_pak_files": "PAK файлы",
    },
}


def get_translation(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"])


def get_available_languages():
    return TRANSLATIONS.keys()
