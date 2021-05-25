import io
import xlsxwriter
import pandas as pd
import random
import string
import zipfile

def simulate_bids(data,
                bid_template,
                SEED,
                NSIMS,
                P_FIELD_ERROR,
                P_EMPTY):

    # Funcion que genera y guarda una oferta completa
    def fill_bid():
        excel_input = pd.ExcelFile(bid_template, engine='openpyxl')
        output_excel = io.BytesIO()
        excel_output = pd.ExcelWriter(output_excel)
        # Llenar las hojas del excel input, una por una.
        for tp in excel_input.sheet_names:
            df = pd.read_excel(excel_input, tp)
            # borrar ultima fila y ultima columna, estan full NAs.
            # quedan así al darles formato (borde superior y borde izquierdo)
            df = df.iloc[:-1, :-1].copy()
            df = df.astype(str)
            for idx, row in df.iterrows():
                # Variables
                zona = row["Zona"]
                model = row["Modelo"]
                data_attributes = data_tps[tp][model]["attributes_asked"]
                # Llenar datos columna a columna
                for column in df.columns:
                    if column not in data_attributes.keys():
                        continue
                    # Lanzar moneda para ver si se cometen errores o no
                    error = True if random.random() <= P_FIELD_ERROR else False
                    empty = True if random.random() <= P_EMPTY else False
                    # Saltar campos vacios
                    if empty:
                        df.at[idx, column] = None
                        continue
                    # Llenar atributos, dependiendo del tipo de atributo
                    data_attribute = data_attributes[column]
                    # Enteros
                    if data_attribute["type"] == "integer":
                        the_range = data_attribute["range"]
                        if error:
                            # error tipo 1: entero fuera de rango
                            if random.random() <= 0.33:
                                while True:
                                    value = random.randint(-9999, 9999)
                                    if value < the_range[0] or value > the_range[1]:
                                        break
                            # error tipo 2: float dentro de rango
                            elif random.random() > 0.33 and random.random() <= 0.66:
                                value = random.randint(the_range[0], the_range[1]) + random.random()
                            # error tipo 3: float fuera de rango
                            else:
                                value = random.randint(-9999, 9999)
                                while True:
                                    value = random.randint(-9999, 9999)
                                    if value < the_range[0] or value > the_range[1]:
                                        break              
                                value += value + random.random()
                        else:
                            value = random.randint(the_range[0], the_range[1])
                    # List con y sin otros
                    elif data_attribute["type"] in ["list","list_others"]:
                        if error:
                            letters = string.ascii_letters
                            value =  ''.join(random.choice(letters) for i in range(10))
                        else:
                            value = random.choice(data_attribute["list"])
                    else:
                        raise ValueError()
                    df.at[idx, column] = value
            # Guardar hoja
            df.to_excel(excel_output,tp, index = False)
        # Guardar excel
        excel_output.save()
        output_excel.seek(0)
        return output_excel

    # Simular NSIMS ofertas
    random.seed(SEED) 
    data_tps = data["products"]

    output = io.BytesIO()
    zip_file = zipfile.ZipFile(output,
                            'w',
                            zipfile.ZIP_STORED)
    for i in range(NSIMS):
        simulation = fill_bid()
        zip_file.writestr("sim{}.xlsx".format(i+1), simulation.getvalue())
    zip_file.close()
    output.seek(0)

    return output
        
