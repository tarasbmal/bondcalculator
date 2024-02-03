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
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([1,2,1])
with col2:    
    st.subheader("Расчет доходности облигации") 
col1, col2, col3 = st.columns([1,3,1])
with col2:   
    #---------  Описание ------
    st.markdown("Ставка доходности - это значение IRR уравнения:")
col1, col2 = st.columns([2.3,1])
with col1:  
    #------------
    st.latex(r'''   
            0 = \sum_{n=0}^{N}
                \frac{CF_n}{\left(1+IRR\right)^{\left(Date_n-Today\right)/365}}
        ''')
col1, col2, col3 = st.columns([1,3,1])
with col2:  
    st.markdown(", где $CF_n$ и $Date_n$  -  сумма и дата n-го потока.")
    st.markdown("Алгоритм аналогичен логике работы формулы ЧИСТВНДОХ (XIRR) приложения Excel")
    st.markdown("Важно! Расчет пока не работает для облигаций с аммортизацией (погашение частями)")
st.divider()
#------------------------------------------------------------------------------        
#isin = "RU000A103RT2"
isin = "RU000A1041B2"
col1, col2, col3 = st.columns([1,2,1],gap="medium")
with col1: 
    st.markdown("**Введите Рег.№ или ISIN Облигации и нажмите кнопку**")
    isin = st.text_input("Введите ISIN:", value=isin,label_visibility="collapsed")
    #-----------------------------------------------------------------------------------------
    button1 = st.button("Получить данные по облигации")
if st.session_state.get('button') != True:
    st.session_state['button'] = button1 # Saved the state
if st.session_state['button'] == True:
    #--------  получаем данные по облигации ---
    ret, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price, fi_couppl, pl = fi.get_fi_data(isin)
    #st.text("=====================================================================")
    if ret == 0:
        st.text("Не найдены данные по облигации ISIN: " + isin + " !!!")
    elif ret == -1:
        st.text("Облигация " + fi_name + " с переменным купоном. Расчет доходности не представляется возможным (")
    else:
        f_buydate = datetime.datetime.today().date()
        #---- проверяем дату оферты на свежесть
        if fi_offer != '—':
            if datetime.datetime.strptime(fi_offer, "%d-%m-%Y").date() <= f_buydate:
                fi_offer = '—'  
        #----------------  Результаты работы -------------
        #col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.subheader('Облигация "' + fi_name + '"')
            st.markdown("**Дата оферты:         " + fi_offer + "**")
            st.markdown("**Дата погашения: " + fi_mat + "**")
        #------- Вводим параметры расчета -------
        st.divider()
        price = float(fi_price)
        col1, col2, col3 = st.columns([1,2,1],gap="medium")
        with col1: 
            st.markdown("**Введите параметры расчета и нажмите кнопку**")
            price = st.number_input("Цена покупки, %", value=price)
            use_offer = "Погашения"
            if fi_offer != '—':
                use_offer = st.radio("Рассчитывать до даты",["Оферты","Погашения"])     
            use_nalog = st.checkbox('Учитывать подоходный налог 13%', value=True)
            button1 = st.button("Рассчитать доходность")
        if button1:
            #---------   Вычисляем парамеры в нужном формате 
            f_buysum = (float(fi_nominal)*price/100+float(fi_nkd))
            if use_offer == 'Оферты':
                f_enddate = datetime.datetime.strptime(fi_offer, "%d-%m-%Y").date()
            else:
                f_enddate = datetime.datetime.strptime(fi_mat, "%d-%m-%Y").date()
            #----  Преобразовать в дату (без времени)     
            #f_enddate = f_enddate.date()
            #----  Преобразовать сумму
            f_endsum = float(fi_nominal)   
            #---------   Оставляем только все данные до погашения или оферты 
            pl = pl[pl['dates'] <= f_enddate]              
            #------  Если суммы нет, то 0 (ноль)
            pl.loc[pl['amounts'] == "—", 'amounts'] = 0.00
            #------  Устанавливаем правильный тип поля  
            pl[['amounts']] = pl[['amounts']].astype(float)
            #st.text(pl.dtypes)
            #--------  Если купон = 0, ту устанавливаем последний известный 
            amounts_prev = 0
            for index, row in pl.iterrows():
                if row['amounts'] == 0:
                    pl['amounts'].loc[index] = amounts_prev
                    pl['comment'].loc[index] = "Купон(здесь=сумме последнего известного купона)"
                else:
                    amounts_prev = row['amounts']     
            #---- Если купон не до даты погашения тела, то вычисляем 
            last_coup_date = pl['dates'].iloc[-1]  
            if last_coup_date < f_enddate:    
                part_sum = round(float(fi_nominal)*float((f_enddate-last_coup_date).days)*float(fi_couppl)/36500,2)
                pl.loc[len(pl.index)] = [f_enddate, part_sum,"Купон (часть)"]              
            #---------   Добавляем налог с купонов ---
            if use_nalog:
                for index,row in pl.iterrows():
                    if pl['amounts'][index] !=0:
                        pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 'amounts': round(pl['amounts'][index]*(-0.13),2),'comment': "Налог с суммы купона"}, index=[0])],ignore_index=True)                              
                #--- если купили дешевле, то еще в конце срока
                if f_buysum < f_endsum:
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 'amounts': round((f_endsum-f_buysum)*(-0.13),2),'comment': "Налог с разницы сумм погашения и покупки"}, index=[0])],ignore_index=True)                              
            #---------   Добавляем покупку  -----------
            pl.loc[len(pl.index)] = [f_buydate, f_buysum*(-1),"Сумма сделки покупки, включая НКД"]
            #---------   Добавляем погашение -----
            pl.loc[len(pl.index)] = [f_enddate,f_endsum,"Погашение тела облигации"]
            #-------  Запуск расчета ------
            IRR = xirr(pl)
            #st.divider()
            #-------  Только ненулевые суммы  
            rslt_pl = pl[pl['amounts'] != 0] 
            #-------  Перерасчитываем дисконтируемые суммы потоков 
            rslt_pl['d_ams'] = 0
            dams_total = 0
            dur = 0
            for index, row in rslt_pl.iterrows():
                ddelta = (rslt_pl['dates'].loc[index]-f_buydate).days
                dams = rslt_pl['amounts'].loc[index]/((1+IRR)**(ddelta/365))
                rslt_pl['d_ams'].loc[index] = dams
                dams_total = dams_total + dams
                if dams > 0:
                    dur = dur + dams*ddelta
            #----  Дюрация 
            dur = round(dur/f_buysum/365,1)
            #-------  Выводим основные данные ---
            with col2: 
                st.subheader("Доходность: " + str(round(IRR*100,2)) + " %")
                st.markdown("**Дюррация Макколея: " + str(dur) + " лет**")
                dur_m = round(dur/(1+IRR),1)
                st.markdown("**Модифицированная дюррация: " + str(dur_m) + "**")
                #-------  Сортируем и выводим подробности расчета 
                st.divider()
                st.markdown("**Список всех денежных потоков**")     
                rslt_pl2 = rslt_pl.sort_values(by=['dates'])
                rslt_pl2.reset_index(drop= True , inplace= True )     #-- сброс индекса  
                rslt_pl2.columns = ['Дата', 'Сумма', 'Вид суммы', 'Дисконтируемая сумма']   #-- переименовать столбцы
                st.dataframe(rslt_pl2,700)  
            col1, col2 = st.columns([1.5,1])
            with col2: 
                st.markdown("**Итого:       " + str(round(dams_total,2)) + "**")
       #st.text("=====================================================================")
st.divider()
col1, col2 = st.columns([1,1])
with col2:    
    st.text("Тарас Малашенко, e-mail: tarasbmal@gmail.com")
