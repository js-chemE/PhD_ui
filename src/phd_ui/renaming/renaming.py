from pydantic import BaseModel, Field
import pandas as pd
from typing import List, Dict
from pathlib import Path
from os import PathLike

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_SHEETNAME = "Components"

class Renaming(BaseModel):
    filepath: str | Path | PathLike[str] = Field(title="File", description="File that was read to create the data", kw_only=True)
    data: pd.DataFrame | None = Field(default = None, title="Data", description="Data that has been read from the source files")
    sheetname: str = Field(default=DEFAULT_SHEETNAME, title="SheetName", description="Sheet name of the file that was read", kw_only=True)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    def model_post_init(self, _context):
        self.read_file()
    
    def read_file(self):
        raw = pd.read_excel(self.filepath, sheet_name=self.sheetname, header = 0)
        self.data = raw
        
    def get_renaming(self, input_values: str | List[str] | pd.Series) -> str | List[str] | pd.Series:
        if isinstance(input_values, str):
            return self.get_renaming_single(input_values)
        elif isinstance(input_values, list):
            return [self.get_renaming_single(value) for value in input_values]
        elif isinstance(input_values, pd.Series):
            return input_values.apply(self.get_renaming_single)
        else:
            logger.error(f"Input type {type(input_values)} is not supported for get_renamings.")
            return input_values
    
    def get_renaming_single(self, input_value: str) -> str:
        if self.data is None:
            logger.error("Data is not loaded. Cannot perform renaming.")
            return input_value
        
        if input_value in self.data['Set'].values:
            return input_value

        version_columns = [col for col in self.data.columns if col.startswith("Version")]
        for _, row in self.data.iterrows():
            if input_value in row[version_columns].values:
                return row['Set']
    
        logger.warning(f"Input '{input_value}' is not found in 'Set' or any 'Version' columns.")
        return input_value
    
    def as_dict(self) -> Dict[str, str]:
        if self.data is None:
            logger.error("Data is not loaded. Cannot create lookup dictionary.")
            return {}

        # Initialize an empty dictionary
        lookup_dict = {}

        # Identify version columns dynamically
        version_columns = [col for col in self.data.columns if col.startswith("Version")]

        # Iterate through rows and populate the dictionary
        for _, row in self.data.iterrows():
            set_value = row['Set']
            for col in version_columns:
                version_value = row[col]
                if pd.notna(version_value):  # Exclude NaN values
                    if version_value not in lookup_dict:
                        lookup_dict[version_value] = set_value
                    else:
                        logger.warning(
                            f"Duplicate key '{version_value}' found. Keeping the first occurrence."
                        )

        logger.debug(f"Lookup dictionary created with {len(lookup_dict)} entries.")
        return lookup_dict
