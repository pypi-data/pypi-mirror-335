from abc import ABC, abstractmethod
import datetime

import malac.hd.build


__version__ = "1.1.0"

def version():
    if getattr(malac.hd.build, "EXTERNAL_BUILD", None):
        return __version__
    elif hasattr(malac.hd.build, "INTERNAL_BUILD_LABEL"):
        return f"{__version__}+{getattr(malac.hd.build, 'INTERNAL_BUILD_LABEL')}"
    else:
        return f"{__version__}+{datetime.date.today().strftime('%Y%m%d')}-dev"


class ConvertMaster(ABC):
    @abstractmethod
    def convert(self, input, o_module): # TODO:sbe adapt - this is not what is implemented/needed in base classes
        pass
        # return mapping_as_py

# not sure if this class will be needed, it is only unsed inside the into py converted map


class TransformMaster(ABC):
    @abstractmethod
    def transform(self, source_path, target_path):
        pass

# These are the mappings that might be used to generate code
list_m_modules = {
    ".4.fhir.xml": "fhir.r4.generator.structuremap",
    ".4.fhir.json": "fhir.r4.generator.structuremap",
    ".5.fhir.xml": "fhir.r5.generator.structuremap",
    ".5.fhir.json": "fhir.r5.generator.structuremap",
    ".fhir.xml": "fhir.r5.generator.structuremap",
    ".fhir.json": "fhir.r5.generator.structuremap",
    ".xml": "fhir.r5.generator.structuremap",
    ".json": "fhir.r5.generator.structuremap",
    ".4.map": "fhir.r4.generator.fml",
    ".4.fml": "fhir.r4.generator.fml",
    ".5.map": "fhir.r4.generator.fml",
    ".5.fml": "fhir.r4.generator.fml",
    ".map": "fhir.r5.generator.fml",
    ".fml": "fhir.r5.generator.fml"
}

# These are the models that might be used as source/target of a mapping
list_i_o_modules = {
    "http://hl7.org/fhir/4.0/StructureDefinition":"fhir.r4",
    "http://hl7.org/fhir/4.3/StructureDefinition":"fhir.r4",
    "http://hl7.org/fhir/5.0/StructureDefinition":"fhir.r5",
    "http://hl7.org/fhir/StructureDefinition":"fhir.r5",
    "http://hl7.org/fhir/cda/StructureDefinition": {None: "cda.at_ext", "AT": "cda.at_ext", "CH": "cda.ch_ext_pharm", "IT": "cda.it_ext"},
    "http://hl7.org/cda/stds/core/StructureDefinition": {None: "cda.at_ext", "AT": "cda.at_ext", "CH": "cda.ch_ext_pharm", "IT": "cda.it_ext"},
}
