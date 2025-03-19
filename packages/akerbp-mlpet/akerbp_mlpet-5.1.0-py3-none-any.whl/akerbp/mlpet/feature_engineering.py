import warnings
from typing import Any, Dict, List

import numpy as np
import pandas as pd

import akerbp.mlpet.petrophysical_features as petro
import akerbp.mlpet.utilities as utilities


def add_log_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    # TODO: Remove the + 1 in the logs? Should negative values be returned as np.nan or 0?
    """
    Creates columns with log10 of curves. All created columns are suffixed with
    '_log'. All negative values are set to zero and 1 is added to all values. In
    other words, this function is synonymous of numpy's log1p.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate log10 from

    Keyword Args:
        log_features (list, optional): list of column names for the columns that should be
            loggified. Defaults to None
        num_filler (float, optional): value to fill NaNs with. Defaults to None

    Returns:
        pd.DataFrame: New dataframe with calculated log columns
    """
    log_features: List[str] = kwargs.get("log_features", None)
    num_filler: float = kwargs.get("num_filler", None)
    if log_features is not None:
        if num_filler is not None:
            nf_masks = {}
            for col in log_features:
                if pd.isna(num_filler):
                    mask = df[col].isna()
                else:
                    mask = df[col].eq(num_filler)
                nf_masks[col] = mask
                df.loc[nf_masks[col], col] = np.nan
        log_cols = [col + "_log" for col in log_features]
        df[log_cols] = np.log10(df[log_features].clip(lower=0) + 1)
        if num_filler is not None:
            for col, mask in nf_masks.items():
                df.loc[mask, col] = num_filler  # Set back
                df.loc[mask, col + "_log"] = num_filler  # Ensure log corresponds
    return df


def add_gradient_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Creates columns with gradient of curves. All created columns are suffixed with
    '_gradient'.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate gradient from
    Keyword Args:
        gradient_features (list, optional): list of column names for the columns
            that gradient features should be calculated for. Defaults to None.

    Returns:
        pd.DataFrame: New dataframe with calculated gradient feature columns
    """
    gradient_features: List[str] = kwargs.get("gradient_features", None)
    if gradient_features is not None:
        gradient_cols = [col + "_gradient" for col in gradient_features]
        for i, feature in enumerate(gradient_features):
            df[gradient_cols[i]] = np.gradient(df[feature])
    return df


def add_rolling_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Creates columns with centered window/rolling features of curves. All created columns
    are suffixed with '_window_mean' / '_window_max' / '_window_min'.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate rolling features from

    Keyword Args:
        rolling_features (list): columns to apply rolling features to. Defaults to None.
        depth_column (str): The name of the column to use to determine the sampling
            rate. Without this kwarg no rolling features are calculated.
        window (float): The window size to use for calculating the rolling
            features. **The window size is defined in distance**! The sampling rate
            is determined from the depth_column kwarg and used to transform the window
            size into an index based window. If this is not provided, no rolling features are calculated.
        calculate_mean (bool): Whether to calculate the mean of the window. Defaults to True.
        calculate_max (bool): Whether to calculate the max of the window. Defaults to True.
        calculate_min (bool): Whether to calculate the min of the window. Defaults to True.
        calculate_var (bool): Whether to calculate the variance of the window. Defaults to False.
        calculate_norm_dist (bool): Whether to calculate the normalized distance the current point is from the window min and max. Defaults to False.
            calculate_min and calculate_max must be True for this to work.

    Returns:
        pd.DataFrame: New dataframe with calculated rolling feature columns
    """
    rolling_features: List[str] = kwargs.get("rolling_features", None)
    window = kwargs.get("window", None)
    depth_column = kwargs.get("depth_column", None)
    calculate_mean = kwargs.get("calculate_mean", True)
    calculate_max = kwargs.get("calculate_max", True)
    calculate_min = kwargs.get("calculate_min", True)
    calculate_var = kwargs.get("calculate_var", False)
    calculate_norm_dist = kwargs.get("calculate_norm_dist", False)
    if rolling_features is not None and window is not None and depth_column is not None:
        curves_to_drop = []
        sampling_rate = utilities.calculate_sampling_rate(df[depth_column])
        window_size = int(window / sampling_rate)
        if calculate_mean:
            mean_cols = [col + "_window_mean" for col in rolling_features]
            df[mean_cols] = (
                df[rolling_features]
                .rolling(center=True, window=window_size, min_periods=1)
                .mean()
            )
        if calculate_min or calculate_norm_dist:
            min_cols = [col + "_window_min" for col in rolling_features]
            df[min_cols] = (
                df[rolling_features]
                .rolling(center=True, window=window_size, min_periods=1)
                .min()
            )
            if not calculate_min:
                curves_to_drop.extend(min_cols)
        if calculate_max or calculate_norm_dist:
            max_cols = [col + "_window_max" for col in rolling_features]
            df[max_cols] = (
                df[rolling_features]
                .rolling(center=True, window=window_size, min_periods=1)
                .max()
            )
            if not calculate_max:
                curves_to_drop.extend(max_cols)
        if calculate_var:
            var_cols = [col + "_window_var" for col in rolling_features]
            df[var_cols] = (
                df[rolling_features]
                .rolling(center=True, window=window_size, min_periods=1)
                .var()
            )
        if calculate_norm_dist:
            for col in rolling_features:
                df[col + "_window_norm_dist"] = (df[col] - df[col + "_window_min"]) / (
                    df[col + "_window_max"] - df[col + "_window_min"]
                )
        if curves_to_drop:
            df = df.drop(columns=curves_to_drop, errors="ignore")
    return df


def add_sequential_features(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Adds n past values of columns (for sequential models modelling). All created
    columns are suffixed with '_1' / '_2' / ... / '_n'.

    Args:
        df (pd.DataFrame): dataframe to add time features to

    Keyword Args:
        sequential_features (list, optional): columns to apply shifting to. Defaults to None.
        shift_size (int, optional): Size of the shifts to calculate. In other words, number of past values
            to include. If this is not provided, no sequential features are calculated.

    Returns:
        pd.DataFrame: New dataframe with sequential gradient columns
    """
    sequential_features: List[str] = kwargs.get("sequential_features", None)
    shift_size: int = kwargs.get("shift_size", None)
    if sequential_features and shift_size is not None:
        for shift in range(1, shift_size + 1):
            sequential_cols = [f"{c}_{shift}" for c in sequential_features]
            df[sequential_cols] = df[sequential_features].shift(periods=shift)
    return df


def add_petrophysical_features(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Creates petrophysical features according to relevant heuristics/formulas.

    The features created are as follows (each one can be toggled on/off via the
    'petrophysical_features' kwarg)::

        - VPVS = ACS / AC
        - PR = (VP ** 2 * 2 * VS ** 2) / (2 * (VP ** 2 * VS ** 2)) where
        - VP = 304.8 / AC
        - VS = 304.8 / ACS
        - RAVG = AVG(RDEP, RMED, RSHA), if at least two of those are present
        - LFI = 2.95 * ((NEU + 0.15) / 0.6) * DEN, and
            - LFI < *0.9 = 0
            - NaNs are filled with 0
        - FI = (ABS(LFI) + LFI) / 2
        - LI = ABS(ABS(LFI) * LFI) / 2
        - AI = DEN * ((304.8 / AC) ** 2)
        - CALI*BS = CALI * BS, where
            - BS is calculated using the guess_BS_from_CALI function from this
            module it is not found in the pass dataframe
        - VSH = Refer to the calculate_VSH docstring for more info on this
        - diffRes = Refer to the calculate_diffRes docstring for more info on this

    Args:
        df (pd.DataFrame): dataframe to which add features from and to

    Keyword Args:
        petrophysical_features (list): A list of all the petrophysical features
            that should be created (see above for all the potential features
            this method can create). This defaults to an empty list (i.e. no
            features created).

    Returns:
        pd.DataFrame: dataframe with added features
    """
    petrophysical_features: List[str] = kwargs.get("petrophysical_features", None)

    if petrophysical_features is not None:
        # Calculate relevant features
        if "VP" in petrophysical_features:
            df = petro.calculate_VP(df, **kwargs)

        if "VS" in petrophysical_features:
            df = petro.calculate_VS(df, **kwargs)

        if "VPVS" in petrophysical_features:
            df = petro.calculate_VPVS(df)

        if "PR" in petrophysical_features:
            df = petro.calculate_PR(df)

        if "RAVG" in petrophysical_features:
            df = petro.calculate_RAVG(df)

        if "LFI" in petrophysical_features:
            df = petro.calculate_LFI(df, **kwargs)

        if "FI" in petrophysical_features:
            df = petro.calculate_FI(df)

        if "LI" in petrophysical_features:
            df = petro.calculate_LI(df)

        if "AI" in petrophysical_features:
            df = petro.calculate_AI(df)

        if "CALI-BS" in petrophysical_features:
            df = petro.calculate_CALI_BS(df)

        if "VSH" in petrophysical_features:
            df = petro.calculate_VSH(df, **kwargs)

        if "diffRes" in petrophysical_features:
            df = petro.calculate_diffRes(df, **kwargs)

    return df


def add_formations_and_groups(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Adds a FORMATION AND GROUP column to the dataframe based on the well formation
    tops metadata and the depth in the column.

    Note:
        This function requires several kwargs to be able to run. If they are not
        provided a warning is raised and instead the df is returned untouched.

    Note:
        If the well is not found in formation_tops_mapping, the code will
        print a warning and continue to the next well.

    Example:
         For example::

            formation_tops_mapper = {
                "31/6-6": {
                    "group_labels": ['Nordland Group', 'Hordaland Group', ...],
                    "group_labels_chronostrat": ['Cenozoic', 'Paleogene', ...],
                    "group_levels": [336.0, 531.0, 650.0, ...],
                    "formation_labels": ['Balder Formation', 'Sele Formation', ...],
                    "formation_labels_chronostrat": ['Eocene', 'Paleocene', ...],
                    "formation_levels": [650.0, 798.0, 949.0, ...]
                }
                ...
            }

        The above example would classify all depths in well 31/6-6 between 336 &
        531 to belong to the Nordland Group, and the corresponding chronostrat is the Cenozoic period.
        Depths between 650 and 798 are classified to belong to the Balder formation,
        which belongs to the Eocene period.

    Args:
        df (pd.DataFrame): The dataframe in which the formation tops label column
            should be added

    Keyword Args:
        id_column (str): The name of the column of well IDs
        depth_column (str): The name of the depth column to use for applying the
            mappings.
        formation_tops_mapper (dict): A dictionary mapping the well IDs to the
            formation tops labels, chronostrat and depth levels.

    Warning:
        If the mapper is not provided, the function will attempt to retrieve it
        from CDF. This requires that an API key is set in the environment!

    Returns:
        pd.DataFrame: dataframe with additional columns for FORMATION and GROUP
    """
    id_column: str = kwargs.get("id_column", None)
    depth_column: str = kwargs.get("depth_column", "DEPTH")
    formation_tops_mapper: Dict[str, Any] = kwargs.get("formation_tops_mapper", {})

    if depth_column not in df.columns:
        raise ValueError(
            "Cannot add formations and groups metadata without a depth_column! "
            "Please provide a depth_column kwarg to the add_formations_and_groups "
            " specifying which column to use as the depth column."
        )

    if not formation_tops_mapper:
        raise ValueError(
            "No formation tops mapping provided! Please provide a formation_tops_mapper "
            "kwarg to the add_formations_and_groups function."
        )
    df_ = df.copy()
    if id_column is not None and formation_tops_mapper:
        for well, well_df in df_.groupby(id_column):
            try:
                mappings = formation_tops_mapper[well]
            except KeyError:
                df_.loc[well_df.index, ["GROUP", "FORMATION"]] = np.nan
                warnings.warn(
                    f"No formation tops information found for {well}. Setting "
                    "both GROUP and FORMATION to NaN for this well.",
                    stacklevel=2,
                )
                continue

            group_labels, group_chrono, group_levels = (
                mappings.get("group_labels", {}),
                mappings.get("group_labels_chronostrat", {}),
                mappings.get("group_levels", {}),
            )
            formation_labels, formation_chrono, formation_levels = (
                mappings.get("formation_labels", {}),
                mappings.get("formation_labels_chronostrat", {}),
                mappings.get("formation_levels", {}),
            )

            # Handle groups
            if group_labels and group_levels:
                if len(group_levels) == len(group_labels) + 1:
                    df_.loc[well_df.index, "GROUP"] = pd.cut(
                        well_df[depth_column],
                        bins=group_levels,
                        labels=group_labels,
                        include_lowest=True,
                        right=False,
                        ordered=False,
                    ).astype("object")
                else:
                    warnings.warn(
                        f"The group tops information for {well} is invalid! "
                        "Please refer to the docstring of this method to understand "
                        "the format in which formation top mappings should be provided.",
                        stacklevel=2,
                    )
            else:
                warnings.warn(
                    f"No GROUP information found for {well}.",
                    stacklevel=2,
                )

            # Handle formations
            if formation_labels and formation_levels:
                if len(formation_levels) == len(formation_labels) + 1:
                    df_.loc[well_df.index, "FORMATION"] = pd.cut(
                        well_df[depth_column],
                        bins=formation_levels,
                        labels=formation_labels,
                        include_lowest=True,
                        right=False,
                        ordered=False,
                    ).astype("object")
                else:
                    warnings.warn(
                        f"The formation tops information for {well} is invalid! "
                        "Please refer to the docstring of this method to understand "
                        "the format in which formation top mappings should be provided.",
                        stacklevel=2,
                    )
            else:
                warnings.warn(
                    f"No FORMATION information found for {well}.",
                    stacklevel=2,
                )

            # Handle systems - group levels take precedence over formation levels
            if group_chrono and group_levels:
                if len(group_levels) == len(group_chrono) + 1:
                    df_.loc[well_df.index, "SYSTEM_GROUP"] = pd.cut(
                        well_df[depth_column],
                        bins=group_levels,
                        labels=group_chrono,
                        include_lowest=True,
                        right=False,
                        ordered=False,
                    ).astype("object")
                else:
                    warnings.warn(
                        f"The group chrono information for {well} is invalid! "
                        "Please refer to the docstring of this method to understand "
                        "the format in which formation top mappings should be provided.",
                        stacklevel=2,
                    )
            if formation_chrono and formation_levels:
                if len(formation_levels) == len(formation_chrono) + 1:
                    df_.loc[well_df.index, "SYSTEM_FORMATION"] = pd.cut(
                        well_df[depth_column],
                        bins=formation_levels,
                        labels=formation_chrono,
                        include_lowest=True,
                        right=False,
                        ordered=False,
                    ).astype("object")
                else:
                    warnings.warn(
                        f"The formation chrono information for {well} is invalid! "
                        "Please refer to the docstring of this method to understand "
                        "the format in which formation top mappings should be provided.",
                        stacklevel=2,
                    )
            else:
                warnings.warn(
                    f"No SYSTEM information found for {well}.",
                    stacklevel=2,
                )

            # Combine SYSTEM_GROUP and SYSTEM_FORMATION into SYSTEM
            for col in ["SYSTEM_GROUP", "SYSTEM_FORMATION"]:
                if col in df_.columns:
                    if "SYSTEM" not in df_.columns:
                        df_["SYSTEM"] = df_[col]
                    else:
                        df_["SYSTEM"] = df_["SYSTEM"].combine_first(df_[col])
                    df_ = df_.drop(columns=col)
    else:
        raise ValueError(
            "A formation tops label could not be added to the provided dataframe"
            " because some keyword arguments were missing!"
        )
    return df_


def add_trajectories(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """Add trajectory data to the provided dataframe.
    The type of trajectory data added is governed by the keyword argument 'trajectory_type', and
    the default behaviour is to add both wellbore coordinates and vertical depths.

    Args:
        df (pd.DataFrame): input data

    Keyword Args:
        md_column (str): Name of the column containing the measured depth values
            Defaults to None
        id_column (str): Name of the column containing the well names
            Defaults to None
        client (CogniteClient): Cognite client to use for retrieving data from CDF
            Defaults to None
        trajectory_type (str): Type of trajectory data to add. Can be one of 'coordinates' and 'vertical_depths'
            Defaults to None, where both wellbore coordinates and vertical depths are added
        trajectory_mapping (Dict[str, Dict[str, List[float]]]): trajectory mapping to use.
            Defaults to {}, in which the mapping is retrieved from CDF

            For example::

                trajectory_mapping = {
                    "well-name": {
                        "x": [0.0, 1.0, 2.0, ...],
                        "y": [0.0, 1.0, 2.0, ...],
                        "depth_column": [0.0, 1.0, 2.0, ...],
                        "tvd": [0.0, 1.0, 2.0, ...],
                    },
                    ...
                }

                This would interpolate the x, y, and tvd columns for the well-name well
                based on the depth_column column in the dataframe and the corresponding
                depth_column in the mapping.

    Raises:
        ValueError: Due to missing or invalid specification of keyword arguments
        Exception: Generic exception if something fails in retrieval of the trajectory data from CDF

    Returns:
        pd.DataFrame: output data with trajectory columns added
    """
    md_column: str = kwargs.get("md_column", None)
    id_column: str = kwargs.get("id_column", None)
    trajectory_mapping: Dict[str, Dict[str, List[float]]] = kwargs.get(
        "trajectory_mapping", {}
    )

    if id_column is None:
        raise ValueError("No id_column kwarg provided!")
    if not trajectory_mapping:
        raise ValueError(
            "No trajectory_mapping was provided! Please provide a trajectory_mapping "
            "kwarg to the add_trajectory_data function."
        )
    if md_column is not None and id_column is not None:
        df_ = utilities.interpolate_discrete_trajectory_data_along_wellbore(
            df, id_column, md_column, trajectory_mapping=trajectory_mapping
        )
    else:
        raise ValueError(
            "The vertical depths could not be added to the provided dataframe"
            " because required keyword arguments are missing (id_column, md_column).)"
        )
    return df_
