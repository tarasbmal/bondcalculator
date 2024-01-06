import pandas as pd
import numpy as np 
import datetime 
from pyxirr import xirr
import streamlit as st
import fi 
#----------------------------------------------------
#----------------------------------------------------
#-------  Главный модуль ----------------------------        
#----------------------------------------------------
#----------------------------------------------------
isin = "RU000A103RT2"
isin = st.text_input("ISIN", value=isin)
#-----------------------------------------------------------------------------------------
button1 = st.button("Получить данные по облигации")
if st.session_state.get('button') != True:
    st.session_state['button'] = button1 # Saved the state
if st.session_state['button'] == True:
    #--------  получаем данные по облигации ---
    ret, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price, pl = fi.get_fi_data(isin)
    #st.text("=====================================================================")
    if ret == 0:
        st.text("Не найдены данные по облигации ISIN: " + isin + " !!!")
    else:
        #----------------  Результаты работы -------------
        st.title(fi_name)
        st.text("Дата погашения: " + fi_mat)
        st.text("Дата оферты: " + fi_offer)
        st.text("Номинал: " + fi_nominal)
        st.text("НКД: " + fi_nkd)
        #st.text("=====  Цена =====" + fi_price)
        #st.text("=====  Купоны =====")
        #st.text(pl)
        #st.text(pl.dtypes)
        #------- Вводим параметры расчета -------
        price = float(fi_price)
        price = st.number_input("\bold Цена покупки, %", value=price)
        use_offer = "Погашения"
        if fi_offer != '—':
            use_offer = st.radio("Рассчитывать до даты",["Оферты","Погашения"])            
        #use_nalog = st.radio("Учитывать подоходный налог 13% ?",["Да, учитывать","Нет, не учитывать"])
        use_nalog = st.checkbox('Учитывать подоходный налог 13%', value=True)
        button1 = st.button("Рассчитать доходность")
        if button1:
            #---------   Вычисляем парамеры в нужном формате 
            f_buydate = datetime.datetime.today().date()
            f_buysum = (float(fi_nominal)*price/100+float(fi_nkd))
            if use_offer == 'Оферты':
                f_enddate = datetime.datetime.strptime(fi_offer, "%d-%m-%Y")
            else:
                f_enddate = datetime.datetime.strptime(fi_mat, "%d-%m-%Y")
            f_endsum = float(fi_nominal)    
            #---------   Добавляем налог с купонов ---
            if use_nalog:
                for index,row in pl.iterrows():
                        pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 'amounts': round(pl['amounts'][index]*(-0.13),2)}, index=[0])],ignore_index=True)                              
                #--- если купили дешевле, то еще в конце срока
                if f_buysum < f_endsum:
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 'amounts': round((f_endsum-f_buysum)*(-0.13),2)}, index=[0])],ignore_index=True)                              
            #---------   Добавляем покупку  -----------
            pl.loc[len(pl.index)] = [f_buydate, f_buysum*(-1)]
            #---------   Добавляем погашение -----
            pl.loc[len(pl.index)] = [f_enddate,f_endsum]
            #-------  Запуск расчета ------
            rrr = xirr(pl)
            st.title("Доходность: " + str(round(rrr*100,2)) + " %")
            st.text("Подробности расчета")
            #st.text(pl.sort_values(by=['dates']))
            st.text(pl)
    #st.text("=====================================================================")


