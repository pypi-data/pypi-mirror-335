from abc import ABCMeta, abstractmethod
from io import BufferedReader, IOBase

class OutcomeValue:

    """
    Represents a potential outcome with a probability and associated value.

    Attributes:
        Probability (float): A `float` value representing the probability of the outcome.
        Value (any): The value associated with the outcome. Can be any type.
    """

    Probability = 0.0
    Value = None

    def __init__(self, value: any = '', probability: float = 0.0):
        self.Probability = probability
        self.Value = value

class InferenceContextData:

    """
    - Stores context metadata related to an inference request.
    - This is used to save any context across multiple runs of the engine for the same ContextId (i.e. user session).

    Attributes:
        StoredMeta (dict): A dictionary containing key-value pairs representing the stored metadata.
    """

    StoredMeta: dict = {}

    def __init__(self):
        self.StoredMeta = {}

class InferenceRequest:

    """
    Defines the input values, desired outcomes, and context for an inference.

    Attributes:

        InputValues (dict): A dictionary containing key-value pairs representing the input values.
        DesiredOutcomes (list): A list of strings representing the desired outcomes.
        Context (InferenceContextData): An `InferenceContextData` object containing metadata about the inference request
    
    """


    InputValues: dict
    DesiredOutcomes: list
    Context: InferenceContextData = None 
    def __init__(self):
        self.Context = InferenceContextData()
        self.InputValues = {}
        self.DesiredOutcomes = []
    
class InferenceResponse:

    """
    - Represents the response to an inference request, including error messages, additional costs, and outcome values.
    - This can also allow to relay the context wished by the user to be propagated to subsequent runs.

    Attributes:

        ErrorMessages (str): A string containing any error messages encountered during the inference.
        AdditionalInferenceCosts (float): A `float` value representing the additional costs (in US Dollars) incurred during the inference.
        ReInvokeInSeconds (int): Time in seconds to wait before retrying the inference.
        Context (InferenceContextData): An `InferenceContextData` object containing metadata about the inference request and any information required to be used as a context for subsequent runs (Eg. chatbots).
        OutcomeValues (Deprecated) (dict): A dictionary containing key-value pairs representing the outcome values, where the keys are the desired outcome names and the value is a single `OutcomeValue` object.
        Outcomes (dict): A dictionary containing key-value pairs representing the outcome values, where the keys are the desired outcome names and the values are list of `OutcomeValue` objects.
    
    """


    ErrorMessages: str = ''
    AdditionalInferenceCosts: float = 0.0
    ReInvokeInSeconds: int = -1
    Context: InferenceContextData = None
    OutcomeValues: dict = {}
    Outcomes: dict = {}

    def __init__(self):
        self.ErrorMessages = ''
        self.AdditionalInferenceCosts = 0.0
        self.ReInvokeInSeconds = -1
        self.Context = InferenceContextData()
        self.OutcomeValues = {}
        self.Outcomes = {}

class ChainedInferenceRequest:

    """
    - Represents a chained inference request, i.e. chaining another model from the current Engine using the input structure to provide inputs to that model from the current engine. 
    - This is mainly used by the invokeUnityPredictModel method.

    Attributes:

        ContextId (str): A string representing the ID of the context for the chained inference.
        InputValues (dict): A dictionary containing key-value pairs representing the input values for the chained inference.
        DesiredOutcomes (list): A list of strings representing the desired outcomes for the chained inference.
    
    """


    ContextId: str = ''
    InputValues: dict
    DesiredOutcomes: list

    def __init__(self, contextId='', inputValues={}, desiredOutcomes=[]):
        self.ContextId = contextId
        self.InputValues = inputValues
        self.DesiredOutcomes = desiredOutcomes

    
class ChainedInferenceResponse:

    """
    - Represents the response to a chained inference request, including the context ID, request ID, error messages, compute cost, and outcome values.
    - This is mainly used by the invokeUnityPredictModel method.

    Attributes:

        ContextId (str): A string representing the ID of the context for the chained inference.
        RequestId (str): A string representing the ID of the individual inference request within the chain.
        ErrorMessages (str): A string containing any error messages encountered during the chained inference.
        ComputeCost (float): A `float` value representing the compute cost incurred during the chained inference.
        Outcomes (dict): A dictionary containing key-value pairs representing the outcome values for the chained inference.
    
    """

    ContextId: str = ''
    RequestId: str = ''
    ErrorMessages: str = ''
    ComputeCost: float = 0.0
    OutcomeValues: dict = {}
    Outcomes: dict = {}

    def __init__(self):
        self.ContextId = ''
        self.RequestId = ''
        self.ErrorMessages = ''
        self.ComputeCost = 0.0
        self.OutcomeValues = {}
        self.Outcomes = {}

    def getOutputValue(self, outputName: str, index = 0):
        
        """
        Retrieves an output value from the `Outcomes` dictionary.

        Args:
            outputName (str): The name of the desired output.
            index (int, optional): The index of the output value to retrieve. Defaults to 0.

        Returns:
            Any: The retrieved output value, or None if not found.
        """
        
        if self.Outcomes == None:
            return None
        
        if outputName not in self.Outcomes:
            return None
        
        if len(self.Outcomes.get(outputName)) > index:
            if isinstance(self.Outcomes.get(outputName)[index], dict):
                return self.Outcomes.get(outputName)[index].get('value')
            elif isinstance(self.Outcomes.get(outputName)[index], OutcomeValue):
                return self.Outcomes.get(outputName)[index].Value
        else:
            return None

class FileTransmissionObj:

    """
    Represents a file to be transmitted on the UnityPredict platform.

    Attributes:
        FileName (str): The name of the file.
        FileHandle (IOBase): A file-like object representing the file's content.
    """

    FileName: str = ''
    FileHandle: IOBase = None

    def __init__(self, fileName, fileHandle):
        self.FileName = fileName
        self.FileHandle = fileHandle

class FileReceivedObj:

    """
    Represents a file received from the UnityPredict platform.

    Attributes:
        FileName (str): The name of the received file.
        LocalFilePath (str): The local path where the file was saved.
    """

    FileName: str = ''
    LocalFilePath: str = ''

    def __init__(self, fileName, localFilePath):
        self.FileName = fileName
        self.LocalFilePath = localFilePath

class IPlatform:

    """
    Interface for UnityPredict platform-specific operations.

    Defines a set of methods supporeted by the UnityPredict Platform to run the operations.
    """

    __metaclass__ = ABCMeta

    @classmethod
    def version(self): 
        
        """
        Returns the version of the platform implementation.

        Returns:
            str: The version string.
        """

        return "1.0"

    @abstractmethod
    def getModelsFolderPath(self) -> str: 
        
        """
        Provides access to the location of pre-trained models used for inference.

        Returns:
            str: The path to the models folder.
        """
        
        raise NotImplementedError

    @abstractmethod
    def getModelFile(self, modelFileName: str, mode: str = 'rb') -> IOBase: 
        
        """
        Enables loading model files for inference tasks.

        Args:
            modelFileName (str): The name of the model file.
            mode (str, optional): The file open mode. Defaults to 'rb' (read binary).

        Returns:
            IOBase: A file-like object representing the model file.
        """
        
        raise NotImplementedError

    @abstractmethod
    def getRequestFile(self, requestFileName: str, mode: str = 'rb') -> IOBase: 
        
        """
        Facilitates interaction with request files containing input data.

        Args:
            requestFileName (str): The name of the request file.
            mode (str, optional): The file open mode. Defaults to 'rb' (read binary).

        Returns:
            IOBase: A file-like object representing the request file.
        """
        
        raise NotImplementedError

    @abstractmethod
    def saveRequestFile(self, requestFileName: str, mode: str = 'wb') -> IOBase: 
        
        """
        - Allows creating files on the UnityPredict platform.
        - This will be used for creating intermediate files or output files (text, images, audios, etc.) depending on the application of engine.

        Args:
            requestFileName (str): The name of the request file.
            mode (str, optional): The file open mode. Defaults to 'wb' (write binary).

        Returns:
            IOBase: A file-like object representing the saved file.
        """

        raise NotImplementedError

    @abstractmethod
    def getRequestFilePublicUrl(self, requestFileName: str) -> str: 
        
        """
        Retrieves the public URL of a request file that has been uploaded as an input to the UnityPredict platform. 

        Args:
            requestFileName (str): The name of the request file.

        Returns:
            str: The public URL of the request file.
        """
        
        raise NotImplementedError

    @abstractmethod
    def getLocalTempFolderPath(self) -> str: 
        
        """
        Provides a location for storing temporary files during processing.

        Returns:
            str: The path to the temporary directory.
        """
        
        raise NotImplementedError

    @abstractmethod
    def logMsg(self, msg: str): 
        
        """
        Enables logging messages on the UnityPredict platform for debugging, monitoring, or informational purposes.

        Args:
            msg (str): The message to be logged under the UnityPredict platform..
        """
        
        raise NotImplementedError

    @abstractmethod
    def invokeUnityPredictModel(self, modelId: str, request: ChainedInferenceRequest) -> ChainedInferenceResponse: 
        
        """
        - This method is crucial for invoking UnityPredict models from another AppEngine.
        - This allows the re-usage of a functionality of a model without re-writing the EntryPoint for a similar task that might be required for the intended engine.

        Args:
            modelId (str): The ID of the UnityPredict model to invoke.
            request (ChainedInferenceRequest): A ChainedInferenceRequest object representing the inference request to the chained model indicated by the modelId.

        Returns:
            ChainedInferenceResponse: The response from the UnityPredict model.
        """
        
        raise NotImplementedError


# test = ChainedInferenceResponse()
# test.Outcomes = {
#     'outcome': [OutcomeValue('hello', 0)]
# }

# print(test.getOutputValue('outcome'))