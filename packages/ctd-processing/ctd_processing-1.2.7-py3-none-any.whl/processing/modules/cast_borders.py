from pathlib import Path
from typing import Tuple
from seabirdfilehandler import CnvFile
import pandas as pd
import argparse as arg
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import datetime


def get_cast_borders(file: Path | str) -> Tuple[int, int, int, int]:
    """A function that returns the border dimensions of a cast in a given cnv
    file.

    Parameters
    ----------
    file: Path | str :
        the file path to the target cnv file

    Returns
    -------

    """
    cnv = CnvFile(file)

    df = cnv.create_dataframe()

    # bad_flag = cnv._extract_data_header_meta_info()
    # print(bad_flag)

    try:
        prDM_list = df["prDM"].to_numpy().astype(float)
    except KeyError:
        prDM_list = df["depSM"].to_numpy().astype(float)

    smooth_velo = get_smooth_velo(prDM_list)
    ind_dc_end = get_downcast_end(prDM_list, smooth_velo)  # index downcast end
    ind_dc_start = get_downcast_start(
        ind_dc_end, smooth_velo, prDM_list
    )  # index downcast start
    ind_uc_start = get_upcast_start(ind_dc_end, smooth_velo)
    ind_uc_end = get_upcast_end(ind_dc_end, smooth_velo)  # index upcast end

    if args.verbosity >= 2:
        try:
            Path("../QC").mkdir()
        except FileExistsError:
            pass
        except PermissionError:
            print("No permission to create directory")

        fig = plot_stuff(
            smooth_velo,
            prDM_list,
            [ind_dc_start, ind_dc_end, ind_uc_start, ind_uc_end],
        )
        fig.savefig(
            f"../QC/{Path(file).stem}  {datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")}.png",
            dpi=500,
        )

    elif args.verbosity >= 1:
        print((ind_dc_start, ind_dc_end, ind_uc_start, ind_uc_end))

    CB_list = cast_borders_to_list(
        ind_dc_start, ind_dc_end, ind_uc_start, ind_uc_end, len(df)
    )

    if args.flag:
        CB_list = cast_borders_to_list(
            ind_dc_start, ind_dc_end, ind_uc_start, ind_uc_end, len(df)
        )
        return CnvFile(mark_cast_borders(CB_list, df)).to_cnv(
            f"{Path(file).stem}.cnv"
        )
    else:
        cut_cast_borders(CB_list, df)
        print(
            cnv.to_cnv(
                f"{Path(file).stem}.cnv",
                use_current_df=False,
                use_current_processing_header=True,
            )
        )
        return cnv.to_cnv(
            f"{Path(file).stem}.cnv",
            use_current_df=True,
            use_current_processing_header=True,
        )


def cast_borders_to_list(
    downcast_start: int,
    downcast_end: int,
    upcast_start: int,
    upcast_end: int,
    length: int,
) -> list:
    CB_list = [0] * length
    flag_value = -9.99e-29  # todo - aus den Metadaten Auslesen - wie?
    for i in range(length):
        if (
            i <= downcast_start
            or i > upcast_end
            or downcast_end <= i < upcast_start
        ):
            CB_list[i] = flag_value
    return CB_list


def cut_cast_borders(CB_list: list, df: pd.DataFrame) -> pd.DataFrame:
    index_list = []
    for i in range(len(CB_list)):
        if CB_list[i] < 0:
            index_list.append(i)

    df = df.drop(index_list)

    return df


def mark_cast_borders(CB_list: list, df: pd.DataFrame) -> pd.DataFrame:

    df["flag"] = CB_list

    return df


def get_smooth_velo(prDM_list: np.array) -> np.array:

    # derive velocity from the diffrence in depth over a second
    velo_arr = []
    sampling_rate = 24  # get sampling rate from the metadata
    for i in range(len(prDM_list) - sampling_rate):
        velo_arr.append(prDM_list[i + sampling_rate] - prDM_list[i])

    # apply an butterworth filter and an zero phase filter to velocity
    b, a = sp.signal.butter(3, 0.003)
    smooth_velo = sp.signal.filtfilt(b, a, velo_arr)

    return smooth_velo


def plot_stuff(smooth_velo: np.array, prDM_list: np.array, cast_borders: list):

    figure, axis = plt.subplots(2, 1)

    for i in range(len(cast_borders)):
        axis[0].vlines(
            x=cast_borders[i],
            ymin=np.min(smooth_velo),
            ymax=np.max(smooth_velo),
            colors="red",
            label="vline_multiple - full height",
        )
        axis[1].vlines(
            x=cast_borders[i],
            ymin=np.min(prDM_list),
            ymax=np.max(prDM_list),
            colors="red",
            label="vline_multiple - full height",
        )

    axis[0].plot(smooth_velo)
    axis[1].plot(prDM_list)

    return figure


def get_downcast_end(
    prDM_list: np.array, smooth_velo: np.array
) -> int:  # geht das genauer?

    max_pressure_index = np.argmax(prDM_list)
    max_pressure = prDM_list[max_pressure_index]

    search_index = 0
    for i in range(max_pressure_index, 0, -1):
        if prDM_list[i] <= max_pressure * 0.95:
            search_index = i
            break
    for i in range(search_index, len(smooth_velo)):
        if smooth_velo[i] <= 0:
            return i


def get_downcast_start(
    ind_dc_end: int, smooth_velo: np.array, prDM_list: np.array
) -> int:
    downcast_velo_mean = np.mean(
        smooth_velo[0:ind_dc_end]
    )  # average dowcast velocity

    ind_dc_start = -1

    for i in range(int(ind_dc_end / 2)):
        # when the current velocity is at 15% of the average velocity in the sector between cast start and dowcast end mark the index as dowcast start
        if ind_dc_start < 0 and smooth_velo[i] > downcast_velo_mean * 0.15:
            ind_dc_start = i

        # if the current velocity is at or below 0 after already indexing the downcast start, reset the index
        if ind_dc_start >= 0 and smooth_velo[i] <= 0:
            ind_dc_start = -1
    return ind_dc_start


def get_upcast_start(ind_dc_end: int, smooth_velo: np.array) -> int:
    upcast_velo_mean = np.mean(smooth_velo[ind_dc_end : len(smooth_velo)])
    for i in range(ind_dc_end, len(smooth_velo)):
        if smooth_velo[i] < upcast_velo_mean * 0.5:
            return i


def get_upcast_end(ind_dc_end: int, smooth_velo: np.array) -> int:
    upcast_velo_mean = np.mean(smooth_velo[ind_dc_end : len(smooth_velo)])
    for i in range(len(smooth_velo) - 1, ind_dc_end, -1):
        if smooth_velo[i] < upcast_velo_mean * 0.5:
            return i


if __name__ == "__main__":
    parser = arg.ArgumentParser()
    parser.add_argument(
        "-f",
        "--flag",
        help="Returns .cnv with bad scans flagged",
        action="store_true",
    )
    parser.add_argument(
        "file", help=".cnv file for which cast borders are to be determined"
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )  # -v gib borders aus, -vv plots in ordner speichern
    args = parser.parse_args()

    get_cast_borders(args.file)

    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\high_start_pressure.cnv"))
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\long_slow.cnv"))
    # get_cast_borders("C:\Projects\cast_borders\seabird_example_data\cnv\\meteor_long_slow.cnv")
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\negative_start_depth.cnv"))
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\long_soaking.cnv"))
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\multiple_soaking.cnv"))
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\\very_long.cnv"))
    # get_cast_borders(Path("C:\Projects\cast_borders\seabird_example_data\cnv\constant_pressure.cnv"))
    pass
