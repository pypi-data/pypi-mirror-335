from pathlib import Path
import pandas as pd
import numpy as np
import logging
import seabirdscientific.processing as sbs
from seabirdfilehandler.datatablefiles import CnvFile
from processing.module import ArrayModule

logger = logging.getLogger(__name__)


class AlignCTD(ArrayModule):
    def __call__(
        self,
        input: Path | str | CnvFile | pd.DataFrame | np.ndarray,
        parameters: dict = {},
        name: str = "",
        output: str = "cnvobject",
        output_name: str | None = None,
    ) -> None | CnvFile | pd.DataFrame | np.ndarray:
        return super().__call__(input, parameters, name, output, output_name)

    def transformation(self) -> np.ndarray:
        assert len(self.parameters) > 0
        for key, value in self.parameters.items():
            if key not in self.cnv.parameters:
                raise ValueError(
                    f"Column {key} not in CnvFile {self.cnv.path_to_file}."
                )
            index = [
                index
                for index, param in enumerate(self.cnv.parameters)
                if param == key
            ][0]
            self.array[:, index] = sbs.align_ctd(
                x=self.array[:, index],
                offset=float(value),
                sample_interval=self.sample_interval,
            ).round(decimals=4)
        return self.array
