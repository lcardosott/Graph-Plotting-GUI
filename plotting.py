import matplotlib.pyplot as plt
import pandas as pd

def find_extension(path):
    """
    Find the extension of the file
    """
    return path.split('.')[-1]

def load_data(file_path):
    """
    Analyze the data and return a pandas DataFrame
    """
    extension = find_extension(file_path)
    if extension == 'csv':
        df = pd.read_csv(file_path, index_col=0)
    elif extension == 'xlsx':
        df = pd.read_excel(file_path, index_col=0)
    else:
        return pd.DataFrame()
    

    x_unit = df.index.name.split('(')[1].split(')')[0]
    df.index.name = df.index.name.split('(')[0]

    y_unit = df.columns[1].split('(')[1].split(')')[0]
    file_name = file_path.split('/')[-1]
    file_name = file_name.split('.')[0]

    df.columns = df.columns.str.replace(r'\(.*\)', '', regex=True)
    return df, x_unit, y_unit, file_name
    
def plot_data(data, channels, threshold, x_unit, y_unit, file_name):
    """
    Plot the data
    """
    data = cut_borders(data, threshold) 

    # Configurar a figura do Matplotlib
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.set_title(f"{file_name}")
    ax.set_xlabel(f"{data.index.name} ({x_unit})")
    ax.set_ylabel(f"({y_unit})")
    print(channels)
    for channel in channels:
        if channel['selected']:
            ax.plot(data.index, data[channel['column_name']], label=channel['column_name'], color=channel['column_color'])

    # Adicionar a legenda
    ax.legend(title="Channels", loc="best")

    return fig, data

def cut_borders(data, threshold):
    """
    Cut the start and the end from a Pandas DF, based on a threshold
    """
    if data.empty:
        return data

    min_value = data.index.min()
    max_value = data.index.max()
    print(min_value, max_value)
    cropped_data = data[(data.index >= min_value + threshold) & (data.index <= max_value - threshold)]

    print(cropped_data)
    return cropped_data
