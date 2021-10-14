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
                P_EMPTY,
                P_EDIT_FIELD):

    # Funcion que genera y guarda una oferta completa
    def fill_bid():
        excel_input = pd.ExcelFile(bid_template, engine='openpyxl')
        output_excel = io.BytesIO()
        excel_output = pd.ExcelWriter(output_excel)
        bidattributes = list(data["bidattributes"].keys())
        tps = list(data["products"].keys())

        # Hojas atributos convenio
        for bidattribute in bidattributes:
            sheet_name = bidattribute
            df = pd.read_excel(excel_input, sheet_name)
            # borrar ultima fila y ultima columna, estan full NAs.
            # quedan así al darles formato (borde superior y borde izquierdo)
            df = df.iloc[:-1, :-1].copy()
            df = df.astype(str)
            for idx, row in df.iterrows():
                # Variables
                zona = row["ZONA"]
                nivel = row["NIVEL"]
                minvalue = data_bidattributes[bidattribute]["values"][nivel][zona]["minprice"]
                maxvalue = data_bidattributes[bidattribute]["values"][nivel][zona]["maxprice"]
                the_range = [minvalue, maxvalue]

                # Columna precio
                price_column = df.columns[2]

                # Edit error
                for column in list(df.columns):
                    if column == price_column:
                        continue
                    edit_error = True if random.random() <= P_EDIT_FIELD else False
                    if edit_error:
                        letters = string.ascii_letters
                        value =  ''.join(random.choice(letters) for i in range(10))
                        df.at[idx,column] = value
                    continue

                # Empty error
                empty_error = True if random.random() <= P_EMPTY else False
                if empty_error:
                    df.at[idx, price_column] = None
                    continue

                # Field error
                field_error = True if random.random() <= P_FIELD_ERROR else False
                if edit_error:
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
                    df.at[idx, price_column] = value
                    continue

                # No error
                value = random.randint(the_range[0], the_range[1])
                df.at[idx, price_column] = value
                

            # Guardar hoja
            df.to_excel(excel_output,sheet_name, index = False)

        # Hojas TP
        for n_tp, tp in enumerate(tps) :
            n_tp = n_tp + 1 
            sheet_name = "TP{} - {}".format(n_tp, tp)
            df = pd.read_excel(excel_input, sheet_name)
            # borrar ultima fila y ultima columna, estan full NAs.
            # quedan así al darles formato (borde superior y borde izquierdo)
            df = df.iloc[:-1, :-1].copy()
            df = df.astype(str)
            for idx, row in df.iterrows():
                # Variables
                zona = row["ZONA"]
                model = row["MODELO"]
                data_attributes = data_tps[tp][model][zona]["attributes_asked"]
                # Llenar datos columna a columna
                for column in df.columns:

                    # Edit error
                    if column not in data_attributes.keys():
                        edit_error = True if random.random() <= P_EDIT_FIELD else False
                        if edit_error:
                            letters = string.ascii_letters
                            value =  ''.join(random.choice(letters) for i in range(10))
                            df.at[idx,column] = value
                        continue

                    # Empty error
                    empty_error = True if random.random() <= P_EMPTY else False
                    if empty_error:
                        df.at[idx, column] = None
                        continue

                    # Llenar atributos dependiendo de su tipo y si se comete error al llenarlo o no
                    data_attribute = data_attributes[column]
                    field_error = True if random.random() <= P_FIELD_ERROR else False
                    # Enteros
                    if data_attribute["type"] == "integer":
                        the_range = data_attribute["range"]
                        if field_error:
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
                    # Floats
                    elif data_attribute["type"] == "float":
                        the_range = data_attribute["range"]
                        if field_error:
                            # error tipo 3: float fuera de rango
                            value = random.randint(-9999, 9999)
                            while True:
                                value = random.randint(-9999, 9999)
                                if value < the_range[0] or value > the_range[1]:
                                    break              
                            value += value + random.random()
                        else:
                            value = random.randint(the_range[0], the_range[1])
                            value += value + random.random()
                    # List con y sin otros
                    elif data_attribute["type"] in ["list","list_others"]:
                        if field_error:
                            letters = string.ascii_letters
                            value =  ''.join(random.choice(letters) for i in range(10))
                        else:
                            value = random.choice(data_attribute["list"])
                    else:
                        print(data_attribute["type"])
                        raise ValueError()
                    df.at[idx, column] = value
            # Guardar hoja
            df.to_excel(excel_output,sheet_name, index = False)
        # Guardar excel
        excel_output.save()
        output_excel.seek(0)
        return output_excel

    # Simular NSIMS ofertas
    random.seed(SEED) 
    data_bidattributes = data["bidattributes"]
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
        
