from .from_file_loader import fl_to_csv,fl_to_excel,fl_to_json,fl_to_sqlite


MAPPER = {
    "toolbox.dao.files.loader.FileLoader": {
        "to_json":fl_to_json,
        "to_csv":fl_to_csv,
        "to_sqlite":fl_to_sqlite,
        "to_excel":fl_to_excel,
    },
}