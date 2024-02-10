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
    st.subheader("Доходность облигации") 
col1, col2, col3 = st.columns([1,3,1])
with col2:   
    #---------  Описание ------
    st.markdown("Доходность - это ключевая характеристика облигации. Для ее корректного расчета необходимо учитывать все денежные потоки,")
    st.markdown("связанные с ценной бумагой - сумму покупки, комиссии, купоны, возврат суммы номинала, причем не обязательно в конце срока.")
    st.markdown("Кроме того, если вы приобретаете облигацию как физическое лицо, необходимо учесть подоходный налог на доходы физических лиц.")
    st.markdown("В конечном итоге, решением задачи является нахождение значения переменной IRR уравнения:")
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
    st.markdown("Данный алгоритм работает аналогично формуле ЧИСТВНДОХ (XIRR) Excel")
    #st.markdown("Важно! Расчет пока не работает для облигаций с аммортизацией (погашение частями)")
st.divider()
#------------------------------------------------------------------------------        
col1, col2, col3 = st.columns([1,2,1],gap="medium")
with col1: 
    st.markdown("**Введите Код, Рег.№ или ISIN облигации (например, RU000A1041B2):**")
    sec_code = st.text_input("Введите код облигации:", label_visibility="collapsed")
    #-----------------------------------------------------------------------------------------
    #button1 = st.button("Получить данные по облигации")
#if st.session_state.get('button') != True:
#    st.session_state['button'] = button1 # Saved the state
#if st.session_state['button'] == True:
if sec_code:
    #--------  получаем данные по облигации ---
    sec_id,sec_name,sec_isin,mat_date,offer_date,nom_sum,nom_cur,r_cur,coup_sum,coup_date,coup_prc,coup_period,nkd_sum,set_date,price=fi.micex_get_sec(sec_code)
    if sec_id == "":
	    ret = 0
    else: 
        #-----------  Получаем данные по купонам -------------------------------------
        ret, pl = fi.get_coups(sec_id)
    #-------------------------------------------------------------------------------------
    if ret == 0:
        st.text("Не найдены данные по облигации с введенным кодом: " + sec_code + " !!!")
    elif ret == -1:
        st.text("Облигация " + sec_name + " с переменным купоном. Расчет доходности не представляется возможным (")
    else:
        f_buydate = datetime.datetime.today().date()
        #f_buydate = datetime.datetime(2024, 2, 9).date()
        #----------------  Результаты работы -------------
        with col2:
            st.subheader('Облигация "' + sec_name + '"')
            if offer_date != "":
                st.markdown("**Дата оферты:         " + offer_date.strftime("%d-%m-%Y") + "**")
            #else:
            #   st.markdown("**Дата оферты:      - **")            
            st.markdown("**Дата погашения: " + mat_date.strftime("%d-%m-%Y") + "**")
            st.markdown("**Дата расчетов на бирже: " + set_date.strftime("%d-%m-%Y") + "**")
            st.markdown("**Сумма накопленного купонного дохода (НКД): " + str(nkd_sum) + "**")
        #------- Вводим параметры расчета -------
        st.divider()
        price = float(price)
        col1, col2, col3 = st.columns([1,2,1],gap="medium")
        with col1: 
            st.markdown("**Введите параметры расчета и нажмите кнопку**")
            price = st.number_input("Цена покупки, %", value=price, min_value=5.0, max_value=300.0)
            com_pr = st.number_input("Комиссия при покупке, %", value=0.04, min_value=0.0, max_value=1.0)
            use_offer = "Погашения"
            if offer_date != "":
                use_offer = st.radio("Рассчитывать до даты",["Оферты","Погашения"])     
            use_nalog = st.checkbox('Учитывать подоходный налог 13%', value=True)
            button1 = st.button("Рассчитать доходность")
        if button1:
            #---------   Вычисляем парамеры в нужном формате 
            f_buysum = round(float(nom_sum)*price/100,2)+round(float(nkd_sum),2)
            com_sum = round(f_buysum*com_pr/100,2) 
            if use_offer == 'Оферты':
                f_enddate = offer_date
            else:
                f_enddate = mat_date
            #----  Преобразовать сумму
            f_endsum = float(nom_sum)   
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
                part_sum = round(float(nom_sum)*float((f_enddate-last_coup_date).days)*float(coup_prc)/36500,2)
                pl.loc[len(pl.index)] = [f_enddate, part_sum,"Купон (часть)"]              
            #---------   Добавляем налог с купонов ---
            if use_nalog:
                n = 0
                for index,row in pl.iterrows():
                    if pl['amounts'][index] !=0:
                        n = n + 1
                        if n == 1:
                            #------ для 1-го купона база скорректирована на сумму НКД при покуаке ---
                            pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 'amounts': round((pl['amounts'][index]-nkd_sum)*(-0.13),2),'comment': "Налог с суммы купона за вычетом НКД при покупке"}, index=[0])],ignore_index=True)                              
                        else:                            
                            pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 'amounts': round(pl['amounts'][index]*(-0.13),2),'comment': "Налог с суммы купона"}, index=[0])],ignore_index=True)                              
            #---------   Добавляем покупку  -----------
            pl.loc[len(pl.index)] = [f_buydate, f_buysum*(-1),"Сумма сделки покупки, включая НКД"]
            #---------   Добавляем комиссию   -----------
            if com_sum>0:
                pl.loc[len(pl.index)] = [f_buydate, com_sum*(-1),"Комиссия при покупке"]
            #---------   Добавляем погашение -----
            pl.loc[len(pl.index)] = [f_enddate,f_endsum,"Погашение тела облигации"]
            #--- если купили дешевле, то еще налог - в конце срока
            if use_nalog:
                if f_buysum < f_endsum:
                    y_amount = (f_enddate - f_buydate).days//365    #-- число полных лет до погашения
                    if y_amount < 3:
                        pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 'amounts': round((f_endsum-f_buysum)*(-0.13),2),'comment': "Налог с разницы сумм погашения и покупки"}, index=[0])],ignore_index=True)                              
            #-------  Запуск расчета ------
            IRR = xirr(pl)
            #st.divider()
            #-------  Только ненулевые суммы  
            rslt_pl = pl[pl['amounts'] != 0] 
            #-------  Перерасчитываем дисконтируемые суммы потоков + добавляем столбец даты в нужном формате 
            rslt_pl['d_ams'] = 0
            rslt_pl['str_dates'] = ""
            dams_total = 0
            dur = 0
            for index, row in rslt_pl.iterrows():
                rslt_pl['str_dates'].loc[index] = rslt_pl['dates'].loc[index].strftime("%d-%m-%Y")
                #----------------------------------------------                
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
                #-------  Перерасчитываем дисконтируемые суммы потоков 
                rslt_pl2 = rslt_pl.sort_values(by=['dates'])
                rslt_pl2.reset_index(drop= True , inplace= True )     #-- сброс индекса  
                rslt_pl3 = rslt_pl2[['str_dates','comment','amounts','d_ams']]
                rslt_pl3.columns = ['  Дата','         Вид суммы', '  Сумма','Дисконтируемая сумма']   #-- переименовать столбцы
                st.dataframe(rslt_pl3,700)  
            col1, col2 = st.columns([1,1.7])
            with col2: 
                st.markdown("**Итоговая сумма дисконтируемых денежных потоков:  " + str(round(dams_total,2)) + "**")
            if use_nalog and (f_buysum < f_endsum) and y_amount>=3:
                st.markdown("**Внимание! Длительность инвестиции составило более 3-х лет. В связи с этим, применяется льгота долгосрочного владения (ЛДВ) и налог с разницы суммы погашения и суммы приобретения - не применяется." + "**")
       #-----------------------------------------------------------------------------------------
st.divider()
col1, col2 = st.columns([1,1.2])
with col2:    
    st.text("e-mail: tarasbmal@gmail.com")
