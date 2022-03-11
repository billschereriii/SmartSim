import warnings

msg = "smartsim.tf has been deprecated in favor of smartsim.ml.tf and\n"
msg += "will be removed in a future release. Please update your import statements."
warnings.warn(
    msg,
    DeprecationWarning,
    stacklevel=2,
)

from .._core._install.buildenv import Version_, Versioner
from ..error import SmartSimError
from ..log import get_logger

logger = get_logger(__name__)

vers = Versioner()
TF_VERSION = vers.TENSORFLOW

try:
    import tensorflow as tf

    installed_tf = Version_(tf.__version__)
    assert installed_tf >= "2.4.0"

except ImportError:  # pragma: no cover
    raise ModuleNotFoundError(
        f"TensorFlow {TF_VERSION} is not installed. Please install it to use smartsim.tf"
    ) from None
except AssertionError:  # pragma: no cover
    raise SmartSimError(
        f"TensorFlow >= {TF_VERSION} is required for smartsim.tf, you have {tf.__version__}"
    ) from None


from .utils import freeze_model
