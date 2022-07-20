import typing
from dataclasses import dataclass

@dataclass
class ValueRange():
    min: int | float
    max: int | float


class ProgressBar():
    '''
    Create a progress bar to send in messages

    :param tasks: Number of tasks to be done
    :param prefix: Prefix that is written at the beginning
        of the progress bar
    :param updateRatio: Percentage of completed tasks at which 
        to update the progress bar. Defaults to the optimalUpdateRatio(),
        see it for details. Or use a fixed value between 0.01 (1 %) 
        and 1.0 (100 %)
    :param size: Progress bar size in characters. By default: 10
    :param barCharacters: Characters for displaying progress bar task states
        in the following order: completed, current, not started
    :param htmlMode: True by default, if set to False, then html tags won't 
        be used in progress bar

    You can change this parameters at runtime
    '''
    def __init__(
        self,
        tasks: int,
        prefix: str="",
        updateRatio: typing.Annotated[float, ValueRange(0.01, 1.0)]=0.0,
        size: int=10,
        barCharacters: typing.Tuple[3 * (str, )]=("⣿", "⣆", "⣀"),
        htmlMode: bool=True
    ):
        self.tasks = tasks
        self.prefix = prefix

        if not updateRatio:
            updateRatio = optimalUpdateRatio(tasks)

        self.updateRatio = updateRatio
        self.size = size

        self.barCharacters = barCharacters
        self.htmlMode = htmlMode

        self._done = 0
        self._doneBlock = 0
        self._notFinished = 1

    @property
    def htmlMode(self) -> bool:
        return self._htmlMode

    @htmlMode.setter
    def htmlMode(self, value: bool):
        if value:
            self._barPattern = "{}|{}{}{}| <b>| {} / {} |</b>"
        else:
            self._barPattern = "{}|{}{}{}| | {} / {} |"
        
        self._htmlMode = value

    def get(self) -> str:
        '''
        Returns the current state of the progress bar
        Updates isNotFinished property

        Use this method with update()
        '''
        self._notFinished = 1 if self.tasks > self._done else 0
        
        if not self._notFinished:
            self._done = self.tasks
        
        doneSize = self.size * self._done // self.tasks
        return self._barPattern.format(
            self.prefix, 
            self.barCharacters[0] * (doneSize-self._notFinished), 
            self.barCharacters[1] * self._notFinished, 
            self.barCharacters[2] * (self.size-doneSize), 
            self._done,
            self.tasks
        )

    def update(self, done: int) -> bool:
        '''
        Update progress bar

        :param done: Number of tasks completed in the last operation

        Returns whether the progress bar needs to be updated according to update ratio
        '''
        self._doneBlock += done
        self._done += done

        if self._doneBlock / self.tasks >= self.updateRatio:
            self._doneBlock = 0
            return True

        return False
    
    @property
    def isNotFinised(self) -> bool:
        '''
        Show if the progress bar has been finished
        '''
        return self._notFinished

    def finish(self) -> str:
        '''
        If you want to force the progress bar to complete
        Returns finished progress bar

        Use this method with special property isNotFinished
        '''
        self._done = self.tasks
        return self.get()

    def reset(self):
        '''
        Reset done tasks
        '''
        self._done = 0
        self._doneBlock = 0
        self._notFinished = 1


def optimalUpdateRatio(
    tasks: int, 
    ratio: float=0.1, 
    updateBlockSize: int=50, 
    updatesLimit: int=250,
    accuracy: int=5
) -> float:
    '''
    Finds optimal ProgressBar updateRatio with given limits:

    :param tasks: Number of tasks
    :param ratio: Update ratio to start, number from 0.01 (1 %) to 1.0 (100 %)
    :param updateBlockSize: Number of tasks done when counter need to be updated
    :param updatesLimit: How many times the counter can be updated
    :param accuracy: Value from 1 to 100, 1 is highest accuracy, 100 is lowest
    '''
    if tasks * ratio < updateBlockSize:
        return ratio
    
    accuracy: float = 1 + accuracy / 100

    while True:
        ratioBlockSize = tasks * ratio
        updatesNumber = tasks / ratioBlockSize

        if ratioBlockSize < updateBlockSize:
            ratio = updateBlockSize / tasks
            break
        
        if updatesNumber > updatesLimit:
            ratio = tasks / updatesLimit / tasks
            break
        
        ratio /= accuracy
    
    return ratio
