def get_journals():
    with open('journals.csv', 'r') as f:
        lines = f.readlines()[1:]
    
    for line in lines:
        title, impact_factor = line.split(',')
        yield [title, float(impact_factor)]
