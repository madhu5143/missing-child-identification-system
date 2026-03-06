import traceback
try:
    import test_debug
    test_debug.test_pipeline()
except Exception as e:
    with open("error_log.txt", "w", encoding="utf-8") as f:
        traceback.print_exc(file=f)
