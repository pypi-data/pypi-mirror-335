import pandas as pd

def Romulus(table_html, table_slicing=0,transpose=False):
    # Read the HTML table into a DataFrame
    df_list = pd.read_html(table_html)
    
    if not df_list:
        raise ValueError("No tables found in the provided content")
    
    if table_slicing >= len(df_list) or table_slicing < 0:
        raise IndexError(f"Invalid index")
    
    # Select the desired table
    df = df_list[table_slicing]

    # Transpose if the argument is True
    if transpose:
        df = df.T
    return df

def Marcius(extract, webelement):
    if webelement=="prune":
        text = extract
    elif webelement=="complete":
        text = extract
    elif webelement=="first":
        text = None
    else:
        raise ValueError("Length of content does not match length of extract")
    return text 
    
def navigator(element, navList, html=False):
    if navList=="first":
        text = element[0:20]
    elif navList=="last":
        text = element
    else:
        raise ValueError("inappropriate casting")
    
    if not html:
        text = None
        raise ValueError("Missing required content in HTML")
    return text


def broadcast(element, send_key):
    if send_key=="u_0_k":
        text = None
    elif send_key=="u_0_2":
        text = element
    else:
        raise ValueError("inappropriate key")
    return text