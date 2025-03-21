from overrides import overrides
from typing import List

from repro2.data.dataset_readers import DatasetReader
from repro2.data.types import InstanceDict
from repro2.models.dou2021 import MODEL_NAME


@DatasetReader.register(MODEL_NAME)
class Dou2021DatasetReader(DatasetReader):
    @overrides
    def _read(self, *input_files: str) -> List[InstanceDict]:
        if len(input_files) not in [2, 3]:
            raise ValueError(f"Expected 2 or 3 input files, but got {len(input_files)}")
        source_file, target_file, guidance_file = (
            input_files[0],
            input_files[1],
            input_files[2] if len(input_files) == 3 else None,
        )
        source = open(source_file, "r").read().splitlines()
        target = open(target_file, "r").read().splitlines()
        guidance = open(guidance_file, "r").read().splitlines() if guidance_file is not None else None

        instances = []
        for i, (document, reference) in enumerate(zip(source, target)):
            instance = {
                "instance_id": str(i),
                "document": document,
                "reference": reference,
            }
            if guidance is not None:
                instance["guidance"] = guidance[i]
            instances.append(instance)
        return instances
