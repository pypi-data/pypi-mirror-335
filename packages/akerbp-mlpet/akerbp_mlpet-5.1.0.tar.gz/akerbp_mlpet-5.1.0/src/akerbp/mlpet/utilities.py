import pickle
import re
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from numpy import float64
from scipy.interpolate import interp1d


def drop_rows_wo_label(df: pd.DataFrame, label_column: str, **kwargs) -> pd.DataFrame:
    """
    Removes columns with missing targets.

    Now that the imputation is done via pd.df.fillna(), what we need is the constant filler_value
    If the imputation is everdone using one of sklearn.impute methods or a similar API, we can use
    the indicator column (add_indicator=True)

    Args:
        df (pd.DataFrame): dataframe to process
        label_column (str): Name of the label column containing rows without labels

    Keyword Args:
        missing_label_value (str, optional): If nans are denoted differently than np.nans,
            a missing_label_value can be passed as a kwarg and all rows containing
            this missing_label_value in the label column will be dropped


    Returns:
        pd.DataFrame: processed dataframe
    """
    missing_label_value = kwargs.get("missing_label_value")
    if missing_label_value is not None:
        return df.loc[df[label_column] != missing_label_value, :]
    return df.loc[~df[label_column].isna(), :]


@lru_cache(maxsize=None)
def read_pickle(path):
    """
    A cached helper function for loading pickle files. Loading pickle files multiple
    times can really slow down execution

    Args:
        path (str): Path to the pickled object to be loaded

    Returns:
        data: Return the loaded pickled data
    """
    infile = Path(path).open("rb")
    data = pickle.load(infile, encoding="bytes")
    infile.close()
    return data


def map_formation_group_system(
    form_or_group_or_system: pd.Series,
    mapping_df: pd.DataFrame,
    missing_value: Union[float, str] = np.nan,
) -> Tuple[Union[float, str], Union[float, str], Union[float, str]]:
    """
    A helper function for retrieving the formation and group of a standardised
    formation/group based on mlpet's NPD pickle mapper.

    Args:
        form_or_group (pd.Series): A pandas series containing AkerBP legal
            formation/group names to be mapped
        mapping_df (pd.DataFrame): A dataframe containing the mapping between
            the AkerBP legal names and the NPD legal names. It must have the following columns:
                - NAME: The standardised lookup slug for the lithostratigraphic unit (the output of the standardize_group_formation_name function)
                - STANDARDIZED_NAME: The SODIR (NPD) legal name for the lithostratigraphic unit
                - PARENT: The SODIR legal parent (group) of the lithostratigraphic unit
                - GRANDPARENT: The SODIR legal grandparent (system) of the lithostratigraphic unit
                - LEVEL: The level of the SODIR (NPD) lithostratigraphic unit (SYSTEM, GROUP, FORMATION, etc.)
        MissingValue (Any): If no mapping is found, return this missing value

    Note:
        GRANDPARENT should always be used for SYSTEMS, PARENT for GROUPS and NAME for FORMATIONS/MEMBERS.

    Returns:
        tuple(pd.Series): Returns a formation and group series respectively corresponding
            to the input string series
    """
    reference = mapping_df.set_index("NAME")
    mapping = {}
    for item in form_or_group_or_system.unique():
        form, group, siistem = missing_value, missing_value, missing_value
        try:
            row = reference.loc[item, :]
            name = row["STANDARDIZED_NAME"]
            parent = row["PARENT"]
            grandparent = row["GRANDPARENT"]
            if row["LEVEL"] == "FORMATION":
                form = name
                group = parent
                siistem = grandparent
            elif row["LEVEL"] == "GROUP":
                group = name
                siistem = grandparent
            elif row["LEVEL"] == "SYSTEM":
                siistem = name
        except KeyError:
            pass
        form, group, siistem = pd.Series([form, group, siistem]).fillna(missing_value)
        mapping[item] = (form, group, siistem)

    form, group, siistem = zip(*form_or_group_or_system.map(mapping))  # type: ignore

    return form, group, siistem


def normalize_group_formation_system(
    df_: pd.DataFrame, mapping_df: pd.DataFrame, add_systems=False
) -> pd.DataFrame:
    """
    A helper function to normalize a GROUP and FORMATION column using mlpet's
    builtin NPD mapper. A SYSTEM column can also optionally be added by setting
    add_systems to True.

    Args:
        add_systems (bool): Whether to add a SYSTEM column to the dataframe based
            on the GROUP and FORMATION columns mapping
        df_ (pd.DataFrame): The dataframe containing both the GROUP and FORMATION
            columns to be normalized
        mapping_df (pd.DataFrame): A dataframe containing the SODIR legal hierarchical mapping
            of lithostratigraphic units. It must have the following columns:
                - NAME: The standardised lookup slug for the lithostratigraphic unit (the output of the standardize_group_formation_name function)
                - STANDARDIZED_NAME: The SODIR (NPD) legal name for the lithostratigraphic unit
                - PARENT: The SODIR legal parent of the lithostratigraphic unit
                - GRANDPARENT: The SODIR legal grandparent of the lithostratigraphic unit
                - LEVEL: The level of the SODIR (NPD) lithostratigraphic unit (SYSTEM, GROUP, FORMATION, etc.)

    Returns:
        pd.DataFrame: The dataframe with the normalization applied
    """
    if "FORMATION" in df_.columns:
        (
            df_["FORMATION"],
            df_["GROUP_MAPPED"],
            df_["SYSTEM_MAPPED_FM"],
        ) = map_formation_group_system(
            df_["FORMATION"].astype(str).apply(standardize_group_formation_name),
            mapping_df,
        )
    if "GROUP" in df_.columns:
        _, df_["GROUP"], df_["SYSTEM_MAPPED_GP"] = map_formation_group_system(
            df_["GROUP"].astype(str).apply(standardize_group_formation_name),
            mapping_df,
        )
        # NOTE: If GROUP is provided to this function and some filling is done,
        # ensure that the FORMATION column is adjusted as well. If a group is
        # inferred, a FORMATION should be set to UNKNOWN unless it was already
        # provided in the FORMATION column sent to this function

        # If formation is aviailable enrich the group column with it
        if "FORMATION" in df_.columns:
            # Special fix for increasing data quality of GROUP column
            fill_index = df_["FORMATION"].ne("UNKNOWN FM") & df_["GROUP"].eq(
                "UNKNOWN GP"
            )
            if fill_index.any():
                df_.loc[fill_index, "GROUP"] = df_.loc[fill_index, "GROUP_MAPPED"]

            # If no group information is available, use the formation mapped groups
            df_["GROUP"] = df_["GROUP"].fillna(df_["GROUP_MAPPED"])
    if add_systems:
        if "SYSTEM" in df_.columns:
            _, _, df_["SYSTEM"] = map_formation_group_system(
                df_["SYSTEM"].astype(str).apply(standardize_group_formation_name),
                mapping_df,
            )
        else:
            df_["SYSTEM"] = np.nan
        for col in ["SYSTEM_MAPPED_GP", "SYSTEM_MAPPED_FM"]:
            if col in df_.columns:
                df_["SYSTEM"] = df_["SYSTEM"].fillna(df_[col])

    df_ = df_.drop(
        columns=["GROUP_MAPPED", "SYSTEM_MAPPED_FM", "SYSTEM_MAPPED_GP"],
        errors="ignore",
    )

    return df_


def standardize_group_formation_name(name: Union[str, Any]) -> Union[str, Any]:
    """
    Performs several string operations to standardize group formation names
    for later categorisation.

    Args:
        name (str): A group formation name

    Returns:
        float or str: Returns the standardized group formation name or np.nan
            if the name == "NAN".
    """

    def __split(string: str) -> str:
        string = string.split(" ")[0]
        string = string.split("_")[0]
        return string

    def __format(string: str) -> str:
        string = string.replace("AA", "A")
        string = string.replace("Å", "A")
        string = string.replace("AE", "A")
        string = string.replace("Æ", "A")
        string = string.replace("OE", "O")
        string = string.replace("Ø", "O")
        return string

    # First perform some formatting to ensure consistencies in the checks
    name = str(name).upper().strip()
    # Replace NAN string with actual nan
    if name == "NAN":
        return np.nan
    # GPs & FMs with no definition leave as is
    unknown = [
        "NO FORMAL NAME",
        "NO GROUP DEFINED",
        "UNDEFINED",
        "UNDIFFERENTIATED",
        "UNKNOWN",
    ]
    for item in unknown:
        if item in name.upper():
            return "UNKNOWN"

    # Remove known prefixes
    known_prefixes = ["LOWER", "MIDDLE", "UPPER", "INTRA"]
    for prefix in known_prefixes:
        if prefix == "INTRA" and "FM" in name:
            name = re.sub("FM.*", "FM", name)
        name = name.replace(prefix, "").strip()

    # Then perform standardization
    if "(" in name and ")" in name:
        # Remove text between parantheses including the parentheses
        name = re.sub(r"[\(].*?[\)]", "", name).strip()
        name = __split(name)
    elif name == "TD":
        name = "TOTAL DEPTH"
    else:
        name = __split(name)

    # Format
    name = __format(name)

    return name


def standardize_names(
    names: List[str], mapper: Dict[str, str]
) -> Tuple[List[str], Dict[str, str]]:
    """
    Standardize curve names in a list based on the curve_mappings dictionary.
    Any columns not in the dictionary are ignored.

    Args:
        names (list): list with curves names
        mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.

    Returns:
        list: list of strings with standardized curve names
    """
    standardized_names = []
    for name in names:
        mapped_name = mapper.get(name)
        if mapped_name:
            standardized_names.append(mapped_name)
        else:
            standardized_names.append(name)
    old_new_cols = {n: o for o, n in zip(names, standardized_names)}
    return standardized_names, old_new_cols


def standardize_curve_names(df: pd.DataFrame, mapper: Dict[str, str]) -> pd.DataFrame:
    """
    Standardize curve names in a dataframe based on the curve_mappings dictionary.
    Any columns not in the dictionary are ignored.

    Args:
        df (pd.DataFrame): dataframe to which apply standardization of columns names
        mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.
            They keys should be the old curve name and the values the desired
            curved name.

    Returns:
        pd.DataFrame: dataframe with columns names standardized
    """
    return df.rename(columns=mapper)


def get_col_types(
    df: pd.DataFrame, categorical_curves: Optional[List[str]] = None, warn: bool = True
) -> Tuple[List[str], List[str]]:
    """
    Returns lists of numerical and categorical columns

    Args:
        df (pd.DataFrame): dataframe with columns to classify
        categorical_curves (list): List of column names that should be considered as
            categorical. Defaults to an empty list.
        warn (bool): Whether to warn the user if categorical curves were
            detected which were not in the provided categorical curves list.

    Returns:
        tuple: lists of numerical and categorical columns
    """
    if categorical_curves is None:
        categorical_curves = []
    cat_original: Set[str] = set(categorical_curves)
    # Make sure we are comparing apples with apples. Sometimes cat_original
    # will contain column names that are no longer in the passed df and this
    # will cause a false positive and trigger the first if check below. So
    # ensure that all cols in cat_original are in the df before proceeding.
    cat_original = {c for c in cat_original if c in df.columns}
    num_cols = set(df.select_dtypes(include="number").columns)
    cat_cols = set(df.columns) - num_cols
    if warn:
        if cat_cols != cat_original:
            extra = cat_original - cat_cols
            if extra:
                warnings.warn(
                    f"Cols {extra} were specified as categorical by user even though"
                    " they are numerical. Note: These column names are the names"
                    " after they have been mapped using the provided mappings.yaml!"
                    " So it could be another column from your original data that"
                    " triggered this warning and instead was mapped to one of the"
                    " names printed above.",
                    stacklevel=2,
                )
            extra = cat_cols - cat_original
            if extra:
                warnings.warn(
                    f"Cols {extra} were identified as categorical and are being"
                    " treated as such. Note: These column names"
                    " are the names after they have been mapped using the provided"
                    " mappings.yaml! So it could be another column from your"
                    " original data that triggered this warning and instead was"
                    " mapped to one of the names printed above.",
                    stacklevel=2,
                )
    cat_cols = cat_original.union(cat_cols)
    # make sure nothing from categorical is in num cols
    num_cols = num_cols - cat_cols
    return list(num_cols), list(cat_cols)


def wells_split_train_test(
    df: pd.DataFrame, id_column: str, test_size: float, **kwargs
) -> Tuple[List[str], List[str], List[str]]:
    """
    Splits wells into two groups (train and val/test)

    NOTE: Set operations are used to perform the splits so ordering is not
        preserved! The well IDs will be randomly ordered.

    Args:
        df (pd.DataFrame): dataframe with data of wells and well ID
        id_column (str): The name of the column containing well names which will
            be used to perform the split.
        test_size (float): percentage (0-1) of wells to be in val/test data

    Returns:
        wells (list): well IDs
        test_wells (list): wells IDs of val/test data
        training_wells (list): wells IDs of training data
    """
    wells = set(df[id_column].unique())
    rng: np.random.Generator = np.random.default_rng()
    test_wells = set(rng.choice(list(wells), int(len(wells) * test_size)))
    training_wells = wells - test_wells
    return list(wells), list(test_wells), list(training_wells)


def df_split_train_test(
    df: pd.DataFrame,
    id_column: str,
    test_size: float = 0.2,
    test_wells: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Splits dataframe into two groups: train and val/test set.

    Args:
        df (pd.Dataframe): dataframe to split
        id_column (str): The name of the column containing well names which will
            be used to perform the split.
        test_size (float, optional): size of val/test data. Defaults to 0.2.
        test_wells (list, optional): list of wells to be in val/test data. Defaults to None.

    Returns:
        tuple: dataframes for train and test sets, and list of test well IDs
    """
    if test_wells is None:
        test_wells = wells_split_train_test(df, id_column, test_size, **kwargs)[1]
        if not test_wells:
            raise ValueError(
                "Not enough wells in your dataset to perform the requested train "
                "test split!"
            )
    df_test = df.loc[df[id_column].isin(test_wells)]
    df_train = df.loc[~df[id_column].isin(test_wells)]
    return df_train, df_test, test_wells


def train_test_split(
    df: pd.DataFrame, target_column: str, id_column: str, **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits a dataset into training and val/test sets by well (i.e. for an
    80-20 split, the provided dataset would need data from at least 5 wells).

    This function makes use of several other utility functions. The workflow it
    executes is:

        1. Drops row without labels
        2. Splits into train and test sets using df_split_train_test which in
            turn performs the split via wells_split_train_test

    Args:
        df (pd.DataFrame, optional): dataframe with data
        target_column (str): Name of the target column (y)
        id_column (str): Name of the wells ID column. This is used to perform
            the split based on well ID.

    Keyword Args:
        test_size (float, optional): size of val/test data. Defaults to 0.2.
        test_wells (list, optional): list of wells to be in val/test data. Defaults to None.
        missing_label_value (str, optional): If nans are denoted differently than np.nans,
            a missing_label_value can be passed as a kwarg and all rows containing
            this missing_label_value in the label column will be dropped

    Returns:
        tuple: dataframes for train and test sets, and list of test wells IDs
    """
    df = drop_rows_wo_label(df, target_column, **kwargs)
    df_train, df_test, _ = df_split_train_test(df, id_column, **kwargs)
    return df_train, df_test


def feature_target_split(
    df: pd.DataFrame, target_column: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits set into features and target

    Args:
        df (pd.DataFrame): dataframe to be split
        target_column (str): target column name

    Returns:
        tuple: input (features) and output (target) dataframes
    """
    X = df.loc[:, ~df.columns.isin([target_column])]  # noqa: N806
    y = df[target_column]
    return X, y


def normalize(
    col: pd.Series, ref_min: float64, ref_max: float64, col_min: float, col_max: float
) -> pd.Series:
    """
    Helper function that applies min-max normalization on a pandas series and
    rescales it according to a reference range according to the following formula:

        ref_low + ((col - col_min) * (ref_max - ref_min) / (col_max - col_min))

    Args:
        col (pd.Series): column from dataframe to normalize (series)
        ref_low (float): min value of the column of the well of reference
        ref_high (float): max value of the column of the well of reference
        well_low (float): min value of the column of well to normalize
        well_high (float): max value of the column of well to normalize

    Returns:
        pd.Series: normalized series
    """
    diff_ref = ref_max - ref_min
    diff_well = col_max - col_min
    with np.errstate(divide="ignore", invalid="ignore"):
        norm = ref_min + diff_ref * (col - col_min) / diff_well
    return norm


def interpolate_discrete_trajectory_data_along_wellbore(
    df: pd.DataFrame,
    id_column: str,
    md_column: str,
    trajectory_mapping: Dict[str, Dict[str, List[float]]],
) -> pd.DataFrame:
    """Linearly interpolate the discrete trajectory data along the entire wellbore

    Args:
        df (pd.DataFrame): input data
        id_column (str): column representing well name
        md_column (str): column representing measured depth
        trajectory_mapping (Dict[str, Dict[str, List[float]]]): trajectory mapping

    Returns:
        pd.DataFrame: output data with interpolated trajectory data as additinoal colmns
    """
    df_ = df.copy()
    for well in trajectory_mapping:
        md_interpolate = df_.loc[df_[id_column] == well, md_column].to_list()
        trajectory_data = trajectory_mapping[well]
        md = trajectory_data[md_column]
        for trajectory_field in trajectory_data.keys():
            if trajectory_field == md_column:
                continue
            trajectory_values = trajectory_data[trajectory_field]
            with warnings.catch_warnings(record=True) as w:
                f = interp1d(x=md, y=trajectory_values, fill_value="extrapolate")
                interpolated_trajectory_values = f(md_interpolate)
            if w:
                warnings.warn(
                    f"Interpolation of {trajectory_field} for well {well} triggered a "
                    f"runtime warning: {w[0].message}",
                    stacklevel=2,
                )
            df_.loc[df_[id_column] == well, trajectory_field] = (
                interpolated_trajectory_values
            )
    return df_


def get_calibration_map(
    df: pd.DataFrame,
    curves: List[str],
    location_curves: List[str],
    mode: str,
    id_column: str,
    levels: Optional[List[str]] = None,
    standardize_level_names: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Returns calibration maps for each level, per well, typically formation and group.
    Calibration maps are pandas dataframes with the well name and unique values for
    each curve and location, where the value is the chosen "mode", such as mean,
    median, mode, etc, specified by the user. Useful for functions
    preprocessors.apply_calibration() and imputers.fillna_callibration_values().

    Args:
        df (pd.DataFrame): dataframe with wells data
        curves (List[str]): list of curves to fetch unique values
        location_curves (List[str]): list of curves indicating location of
        well/formation/group.
        Typically latitude, longitude, tvdbml, depth
        mode (str): any method supported in pandas dataframe for representing the curve,
        such as median, mean, mode, min, max, etc.
        id_column (str): column with well names
        levels (List[str], optional): how to group samples in a well, typically per
        group or formation. Defaults to ["FORMATION", "GROUP"].
        standardize_level_names (bool, optional): whether to standardize formation
        or group names. Defaults to True.

    Returns:
        Dict[str, pd.DataFrame]: dictionary with keys being level and values being the
        calibration map in dataframe format
    """
    if levels is None:
        levels = ["FORMATION", "GROUP"]
    missing_curves = [
        c
        for c in curves + location_curves + levels + [id_column]
        if c not in df.columns
    ]
    if len(missing_curves) > 0:
        raise ValueError(f"Missing necessary curves in dataframe: {missing_curves}")

    if standardize_level_names and any(((c in ["FORMATION", "GROUP"]) for c in levels)):
        for level in levels:
            df[level] = df[level].apply(standardize_group_formation_name)

    level_tables = dict.fromkeys(levels)
    for level in levels:
        data = []
        for w in df[id_column].unique():
            df_well = df[df[id_column] == w]
            for g, s in df_well.groupby(level, dropna=True):
                new_row = [
                    w,
                    g,
                    *getattr(
                        s[curves + location_curves].dropna(how="all"), mode
                    )().to_numpy(),
                ]
                data.append(new_row)
        level_tables[level] = pd.DataFrame(
            data, columns=["well_name", level, *curves, *location_curves]
        )
    return level_tables


def get_calibration_values(
    df: pd.DataFrame,
    curves: List[str],
    location_curves: List[str],
    level: str,
    mode: str,
    id_column: str,
    distance_thres: float = 99999.0,
    calibration_map: Optional[pd.DataFrame] = None,
    standardize_level_names: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Get calibration map and fill na values (if any) for that well
    in calibration maps from closeby wells.

    Args:
        df (pd.DataFrame): dataframe
        curves (List[str]): list of curves to take into account for maps
        location_curves (List[str]): which curves to consider for calculating the distance between wells
        level (str):  how to group samples in a well, typically per group or formation
        mode (str): any method supported in pandas dataframe for representing the curve,
        such as median, mean, mode, min, max, etc.
        id_column (str): column with well names
        distance_thres (float, optional): threshold for indicating a well is to
        far to be considered close enough. Defaults to 99999.0.
        calibration_map (pd.DataFrame, optional): calibration map for the level. Defaults to None.
        standardize_level_names (bool, optional): whether to standardize formation
        or group names. Defaults to True.

    Returns:
        Dict[str, pd.DataFrame]: _description_
    """
    missing_curves = [
        c for c in curves + location_curves + [level, id_column] if c not in df.columns
    ]
    if len(missing_curves) > 0:
        raise ValueError(f"Missing necessary curves in dataframe: {missing_curves}")

    if standardize_level_names and level in ["FORMATION", "GROUP"]:
        df[level] = df[level].apply(standardize_group_formation_name)

    # get closest wells based on location curves
    def get_closest_wells(
        w_name: str,
        well_measures: pd.DataFrame,
        location_curves: List[str],
        calib_map: pd.DataFrame,
        distance_thres: float,
    ) -> Any:
        non_nan_cols = well_measures[location_curves].dropna().index.tolist()
        well_location = well_measures[non_nan_cols].to_numpy()
        nona_rows = calib_map[non_nan_cols].dropna().index
        calib_locations = calib_map.loc[nona_rows, :][non_nan_cols].to_numpy()
        if len(non_nan_cols) < len(location_curves):
            if len(non_nan_cols) == 0:
                warnings.warn(
                    f"There are no valid values for {location_curves}"
                    "in well {w_name} for {well_measures.name}.",
                    stacklevel=2,
                )
                return []
            warnings.warn(
                f"Distance was calculated only with the following features "
                f"{non_nan_cols}, as the rest was missing in well {w_name} "
                f"for {well_measures.name}.",
                stacklevel=2,
            )
        # distance between well and all others:
        calib_map = calib_map.loc[nona_rows, :]
        calib_map["distance"] = np.linalg.norm(
            np.repeat([well_location], repeats=len(calib_map), axis=0)
            - calib_locations,
            axis=1,
        )
        calib_map = calib_map.loc[calib_map["distance"] <= distance_thres, :]
        # TODO: For now only returning 10 closests wells if more than 10 within
        # the distance threshold need to change this to radius based approach (maybe)
        closest_wells = calib_map.sort_values(by="distance")[id_column][:10]
        return closest_wells.tolist()

    # either get calibration from cdf if None or work on given map
    if calibration_map is None:
        # TODO get calibration map from CDF
        raise ValueError("Getting calibration map from CDF not yet implemented!")

    well_values = {}
    for well in df[id_column].unique():
        df_well = df[df[id_column] == well]
        well_properties: Union[Dict[str, float], pd.DataFrame] = {
            g: getattr(v[curves + location_curves].dropna(how="all"), mode)()
            for g, v in df_well.groupby(level)
        }
        well_properties = pd.DataFrame.from_dict(well_properties, orient="index")
        if well_properties.empty:
            warnings.warn(
                f"Well {well} could not be processed (all NaN)!",
                stacklevel=2,
            )
            continue

        # go through each level value, and find closest well
        for i in well_properties.index:
            if not any(well_properties.loc[i, curves].isna()):
                continue
            mask = (calibration_map[id_column] != well) & (calibration_map[level] == i)
            tmp_calib_map = calibration_map.loc[mask, :].copy()
            if not len(tmp_calib_map) > 0:
                continue

            closest_wells = get_closest_wells(
                well,
                well_properties.loc[i],
                location_curves,
                tmp_calib_map,
                distance_thres,
            )
            cwells_map = tmp_calib_map[tmp_calib_map[id_column].isin(closest_wells)]

            if len(closest_wells) == 0:
                continue
            for c in closest_wells:
                well_properties.update(
                    cwells_map.loc[
                        cwells_map[id_column] == c, [level, *curves]
                    ].set_index(level),
                    overwrite=False,
                )
                if all(well_properties.loc[i, curves].notna()):
                    break
        well_values[well] = well_properties
    return well_values


def calculate_sampling_rate(array: pd.Series, max_sampling_rate=1):
    """
    Calculates the sampling rate of an array by calculating the weighed
    average diff between the array's values.

    Args:
        array (pd.Series): The array for which the sampling rate should be calculated
        max_sampling_rate: The maximum acceptable sampling rate above which the
            the calculated sampling rates should not be included in the weighted
            average calculation (defined in unit length/sample e.g. m). Defaults
            to max 1 m per sample (where m is the assumed unit of the provided array)
    """
    if array.empty or array.isna().all():
        raise ValueError(
            "The provided array is empty or contains only NaNs! Cannot calculate sampling rate!"
        )
    diffs = pd.Series(np.diff(array.to_numpy())).value_counts(normalize=True)
    # Ensure big holes in the index don't affect the weighted average
    # Asumming 1 is a good enough threshold for now
    diffs.loc[diffs.index.to_series().abs().gt(max_sampling_rate)] = np.nan
    sampling_rate = (diffs * diffs.index).sum()
    return sampling_rate


def squared_euclidean_distance(
    point_a: npt.NDArray[np.float64], point_b: npt.NDArray[np.float64]
) -> Any:
    """
    Returns the square of the Euclidean distance between two points

    Arguments:
        point_a (np.ndarray): The first point as [depth, x, y]
        point_b (np.ndarray): The second point as [depth, x, y]

    Returns:
        distance (float): The square of the Euclidean distance between point_a
                          and point b
    """
    return np.linalg.norm(point_a - point_b) ** 2


def estimate_parameter(
    depth: List[float],
    x: List[float],
    y: List[float],
    formation: List[str],
    group: List[str],
    parameter_train: List[float],
    depth_train: List[float],
    x_train: List[float],
    y_train: List[float],
    formation_train: List[str],
    group_train: List[str],
    distance_function: Callable[
        [npt.NDArray[np.float64], npt.NDArray[np.float64]], Any
    ] = squared_euclidean_distance,
) -> List[float]:
    """
    Estimates a parameter at given coordinates and zones based on a calibration list of
    parameters with corresponding coordinates and zones.

    Arguments:
        depth (List[float]): List of depths where parameter will be estimated
        x (List[float]): List of x-coordinates where parameter will be estimated
        y (List[float]): List of y-coordinates where parameter will be estimated
        formation (List[str]): List of formations where parameter will be estimated
        group (List[str]): List of groups where parameter will be estimated
        parameter_train (List[float]): Calibration parameter values
        depth_train (List[float]): List of depths for calibration points
        x_train (List[float]): List of x-coordinates for calibration points
        y_train (List[float]): List of y-coordinates for calibration points
        formation_train (List[str]): List of formations for the calibration points
        group_train (List[str]): List of groups for the calibration points
        distance_function (Callable([np.ndarray, np.ndarray], float)): Distance function
                    to use between points in [depth, x, y]

    Return:
        parameters (List[float]): Estimates of the parameter at the given points
    """
    df = pd.DataFrame({
        "DEPTH": depth_train,
        "X": x_train,
        "Y": y_train,
        "FORMATION": formation_train,
        "GROUP": group_train,
        "PARAMETER": parameter_train,
    })
    parameters = []
    for i in range(len(x)):
        # Filter on points in the same formation
        df_compare = df.loc[df.FORMATION == formation[i]]
        if df_compare.shape[0] == 0:
            # If not enough points of matching formation, go for groups
            df_compare = df.loc[df.GROUP == group[i]]
            if df_compare.shape[0] == 0:
                # If not enough points of matching group or formation, use all points
                df_compare = df
        # Compute the distance between the point and all points in
        # the dataframe of comparable calibration points
        point = np.array([depth[i], x[i], y[i]])
        calibration_points = df_compare[["DEPTH", "X", "Y"]].to_numpy()
        calibration_points_parameters = df_compare.PARAMETER.to_numpy()
        distances = np.apply_along_axis(distance_function, 1, calibration_points, point)
        # Remove any points that happen to be at zero distance
        zeros_indexes = [i for i, x in enumerate(distances) if x == 0.0]
        for ind in sorted(zeros_indexes, reverse=True):
            distances = np.delete(distances, ind)
            calibration_points_parameters = np.delete(
                calibration_points_parameters, ind
            )
        # Compute weighted average based on distance
        parameters.append(
            np.sum(1.0 / distances * calibration_points_parameters)
            / np.sum(1.0 / distances)
        )
    return parameters
