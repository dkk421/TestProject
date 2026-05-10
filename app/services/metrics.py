from statistics import median


def calculate_metrics(values: list[float]):
    return {
        "minimum": min(values),
        "maximum": max(values),
        "count": len(values),
        "sum": sum(values),
        "median": median(values)
    }


def build_analytics(stats):
    x_values = [s.x for s in stats]
    y_values = [s.y for s in stats]
    z_values = [s.z for s in stats]

    return {
        "x": calculate_metrics(x_values),
        "y": calculate_metrics(y_values),
        "z": calculate_metrics(z_values)
    }
