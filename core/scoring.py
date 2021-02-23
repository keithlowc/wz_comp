class ScoringSystem:
    '''
    Controls how matches are being scored
    and how to penalize matches depending on
    match kd and team kd

    Expected:

    competition_scoring = {
        'points_per_kill': competition.points_per_kill,
        'points_per_first_place': competition.points_per_first_place,
        'points_per_second_place': competition.points_per_second_place,
        'points_per_third_place': competition.points_per_third_place,
        'points_per_fourth_place': competition.points_per_fourth_place,
        'points_per_fifth_place': competition.points_per_fifth_place,
    }
    '''

    def __init__(self, competition_scoring):
        self.tiers = {
            'bronze_4': 0.26,
            'bronze_3': 0.27,
            'bronze_2': 0.38,
            'bronze_1': 0.47,
            'silver_4': 0.53,
            'silver_3': 0.59,
            'silver_2': 0.64,
            'silver_1': 0.69,
            'gold_4': 0.74,
            'gold_3': 0.78,
            'gold_2': 0.83,
            'gold_1': 0.87,
            'platinum_4': 0.92,
            'platinum_3': 0.97,
            'platinum_2': 1.02,
            'platinum_1': 1.08,
            'diamond_4': 1.14,
            'diamond_3': 1.23,
            'diamond_2': 1.34,
            'diamond_1': 1.54,
            'master': 2.98,
            'legend': 3.57,
        }
        
        self.competition_scoring = competition_scoring
    
    def check_tier_with_kd(self, kd):
        '''
        Checks if the team match was played on 
        a lower tier match and returns penalize
        if true
        '''

        # The team tier is bronze_4
        if kd <= self.tiers['bronze_4']:
            tier = 'bronze_4'
            return tier

        # The team tier is bronze_4
        elif kd > self.tiers['bronze_4'] and kd <= self.tiers['bronze_3']:
            tier = 'bronze_3'
            return tier
        
        # The team tier is bronze_2
        elif kd >= self.tiers['bronze_3'] and kd <= self.tiers['bronze_2']:
            tier = 'bronze_2'
            return tier
        
        # The team tier is bronze_1
        elif kd >= self.tiers['bronze_2'] and kd <= self.tiers['bronze_1']:
            tier = 'bronze_1'
            return tier

        # The team tier is silver_4
        elif kd >= self.tiers['bronze_1'] and kd <= self.tiers['silver_4']:
            tier = 'silver_4'
            return tier

        # The team tier is silver_3
        elif kd >= self.tiers['silver_4'] and kd <= self.tiers['silver_3']:
            tier = 'silver_3'
            return tier
        
        # The team tier is silver_2
        elif kd >= self.tiers['silver_3'] and kd <= self.tiers['silver_2']:
            tier = 'silver_2'
            return tier

        # The team tier is silver_1
        elif kd >= self.tiers['silver_2'] and kd <= self.tiers['silver_1']:
            tier = 'silver_1'
            return tier

        # The team tier is gold_4
        elif kd >= self.tiers['silver_1'] and kd <= self.tiers['gold_4']:
            tier = 'gold_4'
            return tier
        
        # The team tier is gold_3
        elif kd >= self.tiers['gold_4'] and kd <= self.tiers['gold_3']:
            tier = 'gold_3'
            return tier

        # The team tier is gold_2
        elif kd >= self.tiers['gold_3'] and kd <= self.tiers['gold_2']:
            tier = 'gold_2'
            return tier

        # The team tier is gold_1
        elif kd >= self.tiers['gold_2'] and kd <= self.tiers['gold_1']:
            tier = 'gold_1'
            return tier

        # The team tier is platinum_4
        elif kd >= self.tiers['gold_1'] and kd <= self.tiers['platinum_4']:
            tier = 'platinum_4'
            return tier

        # The team tier is platinum_3
        elif kd >= self.tiers['platinum_4'] and kd <= self.tiers['platinum_3']:
            tier = 'platinum_3'
            return tier

        # The team tier is platinum_2
        elif kd >= self.tiers['platinum_3'] and kd <= self.tiers['platinum_2']:
            tier = 'platinum_2'
            return tier

        # The team tier is platinum_1
        elif kd >= self.tiers['platinum_2'] and kd <= self.tiers['platinum_1']:
            tier = 'platinum_1'
            return tier

        # The team tier is diamond_4
        elif kd >= self.tiers['platinum_1'] and kd <= self.tiers['diamond_4']:
            tier = 'diamond_4'
            return tier

        # The team tier is diamond_3
        elif kd >= self.tiers['diamond_4'] and kd <= self.tiers['diamond_3']:
            tier = 'diamond_3'
            return tier

        # The team tier is diamond_2
        elif kd >= self.tiers['diamond_3'] and kd <= self.tiers['diamond_2']:
            tier = 'diamond_2'
            return tier

        # The team tier is diamond_1
        elif kd >= self.tiers['diamond_2'] and kd <= self.tiers['diamond_1']:
            tier = 'diamond_2'
            return tier
    
        # The team tier is master
        elif kd >= self.tiers['diamond_1'] and kd <= self.tiers['master']:
            tier = 'master'
            return tier
        
        # The team tier is legend
        elif kd >= self.tiers['master'] and kd <= self.tiers['legend']:
            tier = 'legend'
            return tier


    def get_position_from_tier(self, tier_name):
        for position, (key, value) in enumerate(self.tiers.items()):
            if key == tier_name:
                return position

    # Get match rank in position ie: 
    # Math rank silver 2 => pos: 6
    # team rank ie: diamond 4 => pos: 16 -> 16 +- 4 => high wout pts 20, low wout pts 12
    # team rank - match rank => 12 - 6 => went down 6 ranks after tolerance 
    # calculate penalty => team_rank pos wout pts = 12 => 100 / (12 - 1) = 8.33% per rank
    # Penalty score = 6 * 8.33% = 50% - Each point is 50% less

    def get_points_per_kill(self, total_kills):
        '''
        Provides points per total
        kills per game
        '''

        points = total_kills * self.competition_scoring['points_per_kill']

        return points

    
    def get_points_per_placement(self, placement):
        '''
        Provides the points based
        on given placement
        '''

        if placement == 1:
            placement_points = self.competition_scoring['points_per_first_place']
        elif placement == 2:
            placement_points = self.competition_scoring['points_per_second_place']
        elif placement == 3:
            placement_points = self.competition_scoring['points_per_third_place']
        elif placement == 4:
            placement_points = self.competition_scoring['points_per_fourth_place']
        elif placement == 5:
            placement_points = self.competition_scoring['points_per_fifth_place']
        else:
            placement_points = 0
        
        return placement_points
