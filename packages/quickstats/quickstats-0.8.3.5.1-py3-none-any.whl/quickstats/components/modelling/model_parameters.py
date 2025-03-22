from typing import Dict, Optional, Union, List, Tuple

from quickstats.core.typing import ArrayType
from quickstats.core.registries import get_registry, create_registry_metaclass
from quickstats.concepts import RealVariable, RealVariableSet
from .data_source import DataSource

ModelParametersRegistry = get_registry('model_parameters')
ModelParametersRegistryMeta = create_registry_metaclass(ModelParametersRegistry)

ParametersType = Union[
    List[RealVariable],
    Tuple[RealVariable, ...],
    RealVariableSet,
    Dict[str, Union[float, ArrayType]]
]

class ModelParameters(RealVariableSet, metaclass=ModelParametersRegistryMeta):
    """
    A base class for model parameters built on RealVariableSet.

    Attributes
    ----------
    PARAMETER_NAMES : Optional[List[str]]
        Names of the parameters for the model.
    PARAMETER_DESCRIPTIONS : Optional[List[str]]
        Descriptions of the parameters for the model.
    """
    __registry_key__ = "_base"

    PARAMETER_NAMES = None
    PARAMETER_DESCRIPTIONS = None
    
    def __init__(
        self,
        components: Optional[ParametersType] = None,
        name: Optional[str] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize ModelParameters with default components or provided ones.

        Parameters
        ----------
        components : Optional[ParametersType]
            Components for the parameter set. Defaults to those obtained from `get_default`.
        name : Optional[str], optional
            Name of the model parameters. Defaults to the registry key.
        verbosity : Optional[str], optional
            Verbosity level for logging or diagnostics. Defaults to None.
        """
        name = name or self.__registry_key__
        components = components or self.get_default()
        super().__init__(
            components=components,
            name=name,
            verbosity=verbosity,
            **kwargs
        )
        self.validate()
        self._name_map = self.get_name_map()
        self._is_locked = True

    def get_default(self) -> List[RealVariable]:
        """
        Create default RealVariables for the model parameters.

        Returns
        -------
        List[RealVariable]
            A list of RealVariables based on `PARAMETER_NAMES` and `PARAMETER_DESCRIPTIONS`.
        """
        names = self.PARAMETER_NAMES or []
        descriptions = self.PARAMETER_DESCRIPTIONS or [None] * len(names)
        if len(names) != len(descriptions):
            raise ValueError("PARAMETER_NAMES and PARAMETER_DESCRIPTIONS must have the same length.")
        return [RealVariable(name=name, description=description)
                for name, description in zip(names, descriptions)]

    def validate(self) -> None:
        """
        Validate the parameters against the expected number of parameters.

        Raises
        ------
        RuntimeError
            If the number of parameters does not match `PARAMETER_NAMES`.
        """
        nparams = len(self.PARAMETER_NAMES) if self.PARAMETER_NAMES is not None else None
        if nparams is not None and len(self) != nparams:
            raise RuntimeError(f'Model {self.name} expects {nparams} parameters but {len(self)} is given')

    def get_name_map(self) -> Dict[str, str]:
        """
        Generate a mapping between original and current parameter names.

        Returns
        -------
        Dict[str, str]
            A dictionary mapping original names to current names.
        """
        if self.PARAMETER_NAMES is None:
            return {name: name for name in self.names}
        return {orig_name: new_name for orig_name, new_name in zip(self.PARAMETER_NAMES, self.names)}

    def prefit(self, data: DataSource) -> None:
        """
        Perform a prefit operation to initialize parameter values from a data source.

        Parameters
        ----------
        data : DataSource
            The data source to use for the prefit operation.
        """
        pass

def extract_histogram_features(hist: "ROOT.TH1") -> Dict[str, float]:
    """
    Extract relevant features from a histogram.

    Parameters
    ----------
    hist : "ROOT.TH1"
        The histogram to analyze.

    Returns
    -------
    Dict[str, float]
        A dictionary containing extracted features such as position of maximum,
        FWHM bounds, and effective sigma.
    """
    hist_max = hist.GetMaximum()
    hist_bin_pos_max = hist.GetMaximumBin()
    hist_pos_max = hist.GetBinCenter(hist_bin_pos_max)
    hist_pos_FWHM_low = hist.GetBinCenter(hist.FindFirstBinAbove(0.5 * hist_max))
    hist_pos_FWHM_high = hist.GetBinCenter(hist.FindLastBinAbove(0.5 * hist_max))
    hist_sigma_effective = (hist_pos_FWHM_high - hist_pos_FWHM_low) / 2.355
    return {
        "pos_max": hist_pos_max,
        "FWHM_low": hist_pos_FWHM_low,
        "FWHM_high": hist_pos_FWHM_high,
        "sigma_effective": hist_sigma_effective
    }

class GaussianParameters(ModelParameters):
    __registry_key__ = 'Gaussian'
    __registry_aliases__ = ['Gauss', 'RooGaussian']

    PARAMETER_NAMES = ['mean', 'sigma']
    
    def prefit(self, data_source: DataSource) -> None:
        hist: "ROOT.TH1" = data_source.as_histogram()
        features = extract_histogram_features(hist)
        hist.Delete()

        self.get(self._name_map['mean']).set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self.get(self._name_map['sigma']).set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )


class DSCBParameters(ModelParameters):
    
    __registry_key__ = 'DSCB'
    __registry_aliases__ = ['RooTwoSidedCBShape', 'RooDSCB', 'RooDSCBShape']

    PARAMETER_NAMES = [
        'muCBNom',
        'sigmaCBNom',
        'alphaCBLo',
        'nCBLo',
        'alphaCBHi',
        'nCBHi'
    ]
    PARAMETER_DESCRIPTIONS = [
        'Mean of crystal ball',
        'Sigma of crystal ball',
        'Location of transition to a power law on the left',
        'Exponent of power-law tail on the left',
        'Location of transition to a power law on the right',
        'Exponent of power-law tail on the right'
    ]

    def prefit(self, data_source: DataSource) -> None:
        hist: "ROOT.TH1" = data_source.as_histogram()
        features = extract_histogram_features(hist)
        hist.Delete()

        self.get(self._name_map['muCBNom']).set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self.get(self._name_map['sigmaCBNom']).set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self.get(self._name_map['alphaCBLo']).set_data(value=1, range=(0., 5.))
        self.get(self._name_map['nCBLo']).set_data(value=10., range=(0., 200.))
        self.get(self._name_map['alphaCBHi']).set_data(value=1, range=(0., 5.))
        self.get(self._name_map['nCBHi']).set_data(value=10., range=(0., 200.))

class CrystalBallParameters(ModelParameters):
    
    __registry_key__ = 'RooCrystalBall'
    __registry_aliases__ = ['RooCrystalBall_DSCB']

    PARAMETER_NAMES = [
        'muNom',
        'sigmaL',
        'sigmaR',
        'alphaL',
        'nL',
        'alphaR',
        'nR'
    ]
    
    PARAMETER_DESCRIPTIONS = [
        'Mean of crystal ball',
        'Width of the left side of the Gaussian component',
        'Width of the right side of the Gaussian component',
        'Location of transition to a power law on the left',
        'Exponent of power-law tail on the left',
        'Location of transition to a power law on the right',
        'Exponent of power-law tail on the right'
    ]

    def prefit(self, data_source: DataSource) -> None:
        hist: "ROOT.TH1" = data_source.as_histogram()
        features = extract_histogram_features(hist)
        hist.Delete()

        self.get(self._name_map['muNom']).set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self.get(self._name_map['sigmaL']).set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self.get(self._name_map['sigmaR']).set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self.get(self._name_map['alphaL']).set_data(value=1, range=(0., 5.))
        self.get(self._name_map['nL']).set_data(value=10., range=(0., 200.))
        self.get(self._name_map['alphaR']).set_data(value=1, range=(0., 5.))
        self.get(self._name_map['nR']).set_data(value=10., range=(0., 200.))

class BukinParameters(ModelParameters):

    __registry_key__ = 'Bukin'

    __registry_aliases__ = ['RooBukinPdf']

    PARAMETER_NAMES = [
        'Xp',
        'sigp',
        'xi',
        'rho1',
        'rho2'
    ]
    PARAMETER_DESCRIPTIONS = [
        'Peak position',
        'Peak width as FWHM divided by 2*sqrt(2*log(2))=2.35',
        'Peak asymmetry',
        'Left tail',
        'Right tail'
    ]

    def prefit(self, data_source: DataSource) -> Dict[str, "ROOT.RooRealVar"]:
        hist: "ROOT.TH1" = data_source.as_histogram()
        features = extract_histogram_features(hist)
        hist.Delete()
        self.get(self._name_map['Xp']).set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self.get(self._name_map['sigp']).set_data(
            value=features['sigma_effective'],
            range=(0.1, 5 * features['sigma_effective'])
        )
        self.get(self._name_map['xi']).set_data(
            value=0.0,
            range=(-1.0, 1.0)
        )
        self.get(self._name_map['rho1']).set_data(
            value=-0.1,
            range=(-1.0, 0.0)
        )
        self.get(self._name_map['rho2']).set_data(
            value=0.,
            range=(0., 1.0)
        )

class ExpGaussExpParameters(ModelParameters):

    __registry_key__ = 'ExpGaussExp'

    __registry_aliases__ = ['RooExpGaussExpShape']

    PARAMETER_NAMES = [
        'mean',
        'sigma',
        'kLo',
        'kHi'
    ]
    PARAMETER_DESCRIPTIONS = [
        'Mean of EGE',
        'Sigma of EGE',
        'kLow of EGE',
        'kHigh of EGE'
    ]

    def prefit(data_source: Optional[DataSource]=None) -> Dict[str, "ROOT.RooRealVar"]:
        hist: "ROOT.TH1" = data_source.as_histogram()
        features = extract_histogram_features(hist)
        hist.Delete()
        self.get(self._name_map['mean']).set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self.get(self._name_map['sigma']).set_data(
            value=features['sigma_effective'],
            range=(0.1, 5 * features['sigma_effective'])
        )
        self.get(self._name_map['kLo']).set_data(
            value=2.5,
            range=(0.01, 10.0)
        )
        self.get(self._name_map['kHi']).set_data(
            value=2.4,
            range=(0.01, 10.0)
        )

class ExponentialParameters(ModelParameters):

    __registry_key__ = 'Exponential'

    __registry_aliases__ = ['Exp', 'RooExponential']

    PARAMETER_NAMES = [
        'c'
    ]

    PARAMETER_DESCRIPTIONS = [
        'Slope of exponential'
    ]
    
    def prefit(self, data_source: Optional[DataSource]=None) -> Dict[str, "ROOT.RooRealVar"]:
        self.get(self._name_map['c']).set_data(
            value=1,
            range=(-10, 10)
        )

def get(
    source: Union[str, ModelParameters, ParametersType]
) -> ModelParameters:
    if isinstance(source, ModelParameters):
        return source
    if isinstance(source, str):
        cls = ModelParametersRegistry.get(source)
        if cls is None:
            raise ValueError(
                f'No predefined parameters available for the'
                f'functional form: "{source}"'
            )
        return cls()
    return ModelParameters(source)