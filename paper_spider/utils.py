def journal_generator():
    with open('journal.csv', 'r') as f:
        lines = f.readlines()[1:]
    
    for line in lines:
        title, impact_factor = line.split(',')
        yield [title, float(impact_factor)]
