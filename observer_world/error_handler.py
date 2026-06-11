import traceback


def safe_execute(sim, logs, name, func):
    try:
        func(logs)

    except Exception as e:
        error_message = (
            f"ERROR in {name} "
            f"(Day {sim.day}, Hour {sim.hour}): "
            f"{type(e).__name__}: {e}"
        )

        logs.append(error_message)

        if not hasattr(sim, "error_log"):
            sim.error_log = []

        sim.error_log.append(error_message)

        if len(sim.error_log) > 100:
            sim.error_log.pop(0)

        print("\n" + "=" * 60)
        print(error_message)
        traceback.print_exc()
        print("=" * 60)