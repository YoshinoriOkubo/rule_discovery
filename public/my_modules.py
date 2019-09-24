# load history data of world scale
## monthly
def load_world_scale_history_data(from_date=None, to_date=None):
    history_data_path = '../data/world_scale.csv'
    # read data
    dt   = np.dtype({'names': ('date', 'ws'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skiprows=1)
    index = 0
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
    return data[index:]

# load history data of flat rate
## monthly
def load_flat_rate_history_data(from_date=None, to_date=None):
    history_data_path = '../data/flat_rate.csv'
    # read data
    dt   = np.dtype({'names': ('date', 'fr'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skiprows=1)
    index = 0
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
    return data[index:]
