
class DatasetModel(object):
    """An object to model data"""

    def __init__(self, dataset, request):
        """Create DatasetModel object with requested dataset and model type, plus additional request parameters"""
        self.df = dataset
        self.mt = request['modelType']

        print('Initialized new DatasetModel with dataset {0} and model type {1}'.
              format(self.df, self.mt))

