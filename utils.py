def create_arb_matrices(odds, verbose=False):
    '''
    Goes through each event and finds the bookies with the best odds for each possible outcome. Saves the best corresponding
    bookie and odds in an dictionary called arb_matrix for each event and returns a list of arb_matrices

        Parameters:
            odds (dict): json object returned from API
        
        Returns:
            arb_matrices (list): list of arb_matrices with best odds and corresponding bookie
    '''
    arb_matrices = []
    for event in odds:

        if verbose:
            print(f"{event['sport_title']} | {event['home_team']} - {event['away_team']}")
            print('-'*50)

        outcomes = []
        n_outcomes = len(event['bookmakers'][0]['markets'][0]['outcomes'])

        for i in range(n_outcomes):
            outcomes.append(event['bookmakers'][0]
                            ['markets'][0]['outcomes'][i]['name'])

        arb_matrix = {outcome: {'bookies': [], 'price': 0}
                        for outcome in outcomes}
        arb_matrix["name"] = f"({event['sport_title']}) {event['home_team']} - {event['away_team']}"
        bookmakers = event['bookmakers']

        for bookie in bookmakers:
            bookie_name = bookie['title']
            for i in range(n_outcomes):
                # Some bookies might not have all outcomes hence we could have an index error
                try:
                    outcome = bookie['markets'][0]['outcomes'][i]['name']
                    bookie_odds = bookie['markets'][0]['outcomes'][i]['price']
                    current_odds = arb_matrix[outcome]['price']
                    if bookie_odds > current_odds:
                        arb_matrix[outcome]['price'] = bookie_odds
                        arb_matrix[outcome]['bookies'] = [bookie_name]
                except IndexError:
                    continue

            for i in range(n_outcomes):
                try:
                    outcome = bookie['markets'][0]['outcomes'][i]['name']
                    bookie_odds = bookie['markets'][0]['outcomes'][i]['price']
                    current_odds = arb_matrix[outcome]['price']
                    if bookie_odds == current_odds:
                        if bookie_name not in arb_matrix[outcome]['bookies']:
                            arb_matrix[outcome]['bookies'].append(bookie_name)
                except IndexError:
                    continue

        arb_matrices.append(arb_matrix)
    return arb_matrices


def calc_arb(arb_matrix, stake):
    '''
    Calculates if there is an arbitrage opportunity from the best possible odds. If yes, it returns a 
    modified arb_matrix which contains information about the payoff and the betting strategy.

        Parameters:
            arb_matrix (dict): dictionary with best odds and corresponding bookie for the event
            stake (int): how much money you are staking, used to calculate payoffs and betting strategy (100 default)
        
        Returns:
            arb_matrix (list): modified arb_matrix with possible arbirtage payoff and betting strategy if arbitrage is possible
    '''
    arb_matrix = arb_matrix.copy()
    s = 0
    outcomes = list(arb_matrix.keys())
    for outcome in outcomes:
        try:
            s += 1/arb_matrix[outcome]['price']
        except TypeError:
            continue
    if s < 1:
        arb_matrix['arbitrage'] = True
    else:
        arb_matrix['arbitrage'] = False

    if arb_matrix['arbitrage']:
        arb_matrix['nvig'] = 1-s
        payout = round((1+arb_matrix['nvig'])*stake, 2)
        arb_matrix['profit'] = payout-stake
        arb_matrix['strat'] = []
        for outcome in outcomes:
            try:
                bet = round(payout/arb_matrix[outcome]['price'], 2)
                arb_matrix['strat'].append(bet)
            except TypeError:
                continue
    return arb_matrix
