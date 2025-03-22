from cross.transformations import DateTimeTransformer
from cross.transformations.utils.dtypes import datetime_columns


class DateTimeTransformerParamCalculator:
    def calculate_best_params(
        self, x, y, model, scoring, direction, cv, groups, verbose
    ):
        columns = datetime_columns(x)

        if verbose:
            print(f"Datetime columns: {len(columns)}")

        if not columns:
            return None

        datetime_transformer = DateTimeTransformer(columns)
        return {
            "name": datetime_transformer.__class__.__name__,
            "params": datetime_transformer.get_params(),
        }
