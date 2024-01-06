#----------------------------------------------------------------------
#----------------------------------------------------------------------
#-------   Процедура получения данных по облигации с сайта
#----------------------------------------------------------------------
#----------------------------------------------------------------------
def get_fi_data(p_isin):
    import pandas as pd
    import datetime 
    import requests
    from bs4 import BeautifulSoup
    #---- Инициализируем переменные ----
    fi_name = ""
    fi_mat = ""
    fi_offer = ""
    fi_nominal = ""
    fi_nkd = ""
    fi_price = ""
    #-----------------------------------
    url = 'https://smart-lab.ru/q/bonds/' + p_isin
    hdr={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
    response = requests.get(url=url,stream=True, headers=hdr, verify=False)
    st_code = response.status_code
    if st_code != 200:
        return 0, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price,  ""    #-- облигация не найдена
    tabs = pd.read_html(response.text)
    #--------------------------------
    #-----   Купоны -----------------
    #--------------------------------
    df = tabs[0]
    # print(df.dtypes)
    coup = df[["Дата купона","Купон"]]  #-- Оставим только нужные колонки
    coup.columns = ["cd","amounts"] #-- переименуем столбцы
    coup["dates"] = datetime.datetime.today()   #-- Новый столбец даты
    for index,row in coup.iterrows():
        coup['dates'][index] = datetime.datetime.strptime(coup['cd'][index], "%d-%m-%Y")
    coup = coup[["dates","amounts"]]    #-- оставляем только нужные поля
    #---------------------------------------------------------
    #-----------  Поиск параметров облигации ----------------------
    #---------------------------------------------------------
    soup = BeautifulSoup(response.text, "html.parser")  
    divs = soup.find_all("div")
    #---------  Флаги ---------------
    flag_name = 0
    flag_mat = 0 
    flag_offer = 0
    flag_nominal = 0
    flag_nkd = 0
    flag_price = 0
    #--------  Цикл для извлечения параметров ----  
    for div in divs:
        if div.get("class") == ['quotes-simple-table__item']:
            dtext = div.text.strip()
            #-------------------------------------------
            if flag_name == 1:
                flag_name = 0
                fi_name = dtext
                print(fi_name)
            if flag_mat == 1:
                flag_mat = 0
                fi_mat = dtext
            if flag_offer == 1:
                flag_offer = 0
                fi_offer = dtext
            if flag_nominal == 1:
                flag_nominal = 0
                fi_nominal = dtext
            if flag_nkd == 1:
                flag_nkd = 0
                fi_nkd = dtext
                fi_nkd = fi_nkd.split()[0]
            if flag_price == 1:
                flag_price = 0
                fi_price = dtext[0:-1]  #убираем знак %
            #--------------------------------------
            if dtext == "Имя облигации":
                flag_name = 1
            if dtext == "Дата погашения":
                flag_mat = 1
            if "Дата оферты" in dtext:
                flag_offer = 1
            if dtext == "Номинал":
                flag_nominal = 1
            if "НКД" in dtext:
                flag_nkd = 1
            if "Котировка облигации" in dtext:
                flag_price = 1
            #------------------------------------
    return 1, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price, coup    #-- успешное завершение, облигация найдена
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
