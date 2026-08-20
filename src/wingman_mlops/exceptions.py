class FineTuningError(Exception):
    pass


class DatasetValidationError(FineTuningError):
    pass


class HardwareConfigurationError(FineTuningError):
    pass


class TrainingExecutionError(FineTuningError):
    pass


class ModelArtifactError(FineTuningError):
    pass
