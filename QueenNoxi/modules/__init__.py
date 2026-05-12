from QueenNoxi import LOAD, LOGGER, NO_LOAD


def __list_all_modules():
    import glob
    from os.path import basename, dirname, isfile

    # This generates a list of modules in this folder for the * in __main__ to work.
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    to_load = []
    for f in mod_paths:
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py"):
            mod_name = basename(f)[:-3]
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                    if "import telegram" in content or "from telegram" in content or "dispatcher." in content:
                         if "from QueenNoxi import pbot" not in content and "@pbot.on_" not in content:
                             LOGGER.info(f"Skipping legacy module: {mod_name}")
                             continue
                to_load.append(mod_name)
            except Exception as e:
                LOGGER.error(f"Error reading module {mod_name}: {e}")
                continue

    if LOAD or NO_LOAD:
        all_modules = to_load
        to_load = LOAD
        if to_load:
            if not all(
                any(mod == module_name for module_name in all_modules)
                for mod in to_load
            ):
                LOGGER.error("Invalid loadorder names. Quitting.")
                quit(1)

            all_modules = sorted(set(all_modules) - set(to_load))
            to_load = list(all_modules) + to_load

        else:
            to_load = all_modules

        if NO_LOAD:
            LOGGER.info("Not loading: {}".format(NO_LOAD))
            return [item for item in to_load if item not in NO_LOAD]

        return to_load

    return to_load


ALL_MODULES = __list_all_modules()
LOGGER.info("Modules to load: %s", str(ALL_MODULES))
__all__ = ALL_MODULES + ["ALL_MODULES"]
