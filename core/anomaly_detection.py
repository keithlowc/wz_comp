from joblib import load

# Competition rank is based on
# KD minimum limit and maximun

class AnomalyDetection():
    def __init__(self, competition_rank):
        self.competition_rank = competition_rank
        self.model, self.threshold = self.choose_model()
    
    def choose_model(self):
        if self.competition_rank == 'Gold':
            model = load('core/models/gold_model.joblib')
            threshold = 1
            return model, threshold
        elif self.competition_rank == 'Catch_all':
            model = load('core/models/catch_all_model.joblib')
            threshold = 1
            return model, threshold

    def detect_anomalous_match(self, kills):
        anomalous = self.model.decision_function([[kills]])
        match_is_anomalous = False

        if anomalous >= self.threshold:
            print('This amount of kills are anomalous to rank {} by {}'.format(self.competition_rank, anomalous))
            match_is_anomalous = True
            return True
        else:
            return False
