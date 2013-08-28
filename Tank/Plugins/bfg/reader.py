from Tank.Plugins.Aggregator import AbstractReader
from Tank.stepper import info as si


class BFGReader(AbstractReader):

    '''
    Listens results from BFG and provides them to Aggregator
    '''

    def __init__(self, aggregator, bfg):
        AbstractReader.__init__(self, aggregator)
        self.bfg = bfg
        self.steps = map(list, si.status.get_info().steps)

    def get_next_sample(self, force):
        new_data = []
        while not self.bfg.results.empty():
            new_data.append(self.bfg.results.get())
        for cur_time, sample in new_data:
            if not cur_time in self.data_buffer.keys():
                self.data_queue.append(cur_time)
                self.data_buffer[cur_time] = []
            self.data_buffer[cur_time].append(list(sample))
        if self.data_queue and len(self.data_queue) > 1:
            res = self.pop_second()
            res.overall.planned_requests = self.__get_expected_rps()
            return res
        else:
            return None

    def __get_expected_rps(self):
        '''
        Mark second with expected rps
        '''
        while self.steps and self.steps[0][1] < 1:
            self.steps.pop(0)
        
        if not self.steps:
            return 0
        else:
            self.steps[0][1] -= 1
            return self.steps[0][0]