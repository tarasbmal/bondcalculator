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
col1, col2 = st.columns([1.2,1])
with col1:    
    st.subheader("Доходность облигации") 
with col1:   
    #---------  Описание ------
    st.markdown("Доходность облигации - это ключевой показатель при принятии решения о приобретении ценной бумаги.")
    sss = ""
    sss = sss + "Под доходностью понимается годовая % ставка доходности (эффективная % ставка). Этот универсальный и независимый от срока и особенностей погашения показатель позволяет сравнивать различные облигации и другие аналогичные инструменты, такие как, банковские депозиты. "  
    sss = sss + "Для корректного расчета необходимо учитывать все денежные потоки, связанные с ценной бумагой - сумму покупки, комиссии, купоны, погашение суммы номинала, в том числе, частичное. "
    sss = sss + "Кроме того, необходимо учесть подоходный налог на доходы физических лиц. "
    sss = sss + "Также, важно иметь ввиду, что даты реальных денежных потоков будут расходиться с датами расчетов на бирже."
    st.markdown(sss)
    st.markdown("В конечном итоге, для решения задачи необходимо найти значение переменной IRR в следующем уравнении:")
#col1, col2 = st.columns([2.3,1])
with col1:  
    #------------
    st.latex(r'''   
            0 = \sum_{n=0}^{N}
                \frac{CF_n}{\left(1+IRR\right)^{\left(Date_n-Today\right)/365}}
        ''')
#col1, col2, col3 = st.columns([1,3,1])
with col1:  
    st.markdown(", где $CF_n$ и $Date_n$  -  сумма и дата n-го потока.")
    st.markdown("Аналогичный алгоритм заложен в формуле ЧИСТВНДОХ (XIRR) приложения Excel")
    st.divider()
#----   Масссив всех доступных облигаций во фрейм для последующего выбора
sec_all  = fi.micex_get_sec_all(0)
#sec_all.to_csv("sec_all.csv",sep=";")   #-----  Выгрузка в файл для тестирования
#------------------------------------------------------------------------------        
#col1, col2, col3 = st.columns([1,2.2,1],gap="medium")
st.sidebar.markdown("**Введите Код, Рег.№,ISIN или часть наименования облигации и нажмите Enter**")
sec_code = st.sidebar.text_input("Введите код облигации:", label_visibility="collapsed")
#----- Тестовые данные (недокументированная возможность)
if sec_code == "0": # Тестовый режим перебора всех облигаций
    ntest = st.sidebar.number_input("N теста", value=1, min_value=1, max_value=2000)
    i = 0
    for index,row in sec_all.iterrows():
        i = i+1
        if i == ntest:
            sec_code = row['ISIN'] 
elif sec_code == "1": # Обычный случай с офертой 
    sec_code= "RU000A1041B2"
elif sec_code == "2": # С аммортизацией тела - Бизнес-Недвижимость
    sec_code= "RU000A1022G1"
elif sec_code == "3": # С аммортизацией тела (много аммортизаций )
    sec_code= "RU000A107C91"
elif sec_code == "4": # Замещающая
    sec_code= "RU000A1056U0"    
elif sec_code == "5": # Ошибка
    sec_code= "RU000A105AD7"    
#-----  Фильтруем  кодам  ----
sec_filter = sec_all[(sec_all["SECID"] == sec_code) | (sec_all["ISIN"] == sec_code) | (sec_all["REGNUMBER"] == sec_code)]	
if sec_filter.shape[0] == 0:    #-- число записей = 0, т.е. не нашли по номеру, ищем по имени
    sec_filter = sec_all[sec_all["SECNAME"].str.contains(sec_code, case=False)]
if sec_code:
    #-----------------   Выбор из списка  ----------------------------------------
    ppp = st.sidebar.selectbox("Выбрать облигацию", sec_filter['SHORTNAME']+ " ,  " +sec_filter['ISIN'], label_visibility="collapsed")   
    isin = ""
    if ppp != None:     
        isin = ppp[-12:]
    #st.sidebar.text(isin) 
    #st.sidebar.text(ppp) 
    sec_code = isin 
    #--------  получаем данные по облигации ---
    #sec_id,sec_name,sec_isin,mat_date,offer_date,nom_sum,nom_cur,r_cur,coup_sum,coup_date,coup_prc,coup_period,nkd_sum,set_date,price=fi.micex_get_sec(sec_code)
    sec_id,sec_name,sec_isin,mat_date,offer_date,nom_sum,nom_cur,r_cur,coup_sum,coup_date,coup_prc,coup_period,nkd_sum,set_date,price=fi.get_sec_one(sec_filter, isin)
    if sec_id == "":
        st.error("Не найдена облигация с ISIN: " + isin + " !!!")
    else: 
        f_buydate = datetime.datetime.today().date()
        f_s_buydate = set_date 
        #f_buydate = datetime.datetime(2024, 2, 9).date()
        #----------------  Результаты работы -------------
        with col1:
            st.subheader(sec_name) 
            st.markdown("**ISIN: " + sec_isin + "**")
            st.markdown("**Текущий номинал: " + str(int(nom_sum)) + " " + nom_cur + "**")
            if offer_date != "":
                st.markdown("**Дата оферты:         " + offer_date.strftime("%d-%m-%Y") + "**")
            else:
               st.markdown("**Дата оферты:**")            
            if mat_date != "":
                st.markdown("**Дата погашения: " + mat_date.strftime("%d-%m-%Y") + "**")
            else:
                st.markdown("**Дата погашения:**")
            st.markdown("**Дата расчетов на Московской бирже: " + f_s_buydate.strftime("%d-%m-%Y") + "**")
            st.markdown("**Сумма накопленного купонного дохода (НКД): " + str(nkd_sum) + "**")
            st.divider()
        #------- Вводим параметры расчета -------
        #col1, col2, col3 = st.columns([1,2.2,1],gap="medium")
        #with col1: 
        st.sidebar.divider()
        st.sidebar.markdown("**Введите параметры расчета и нажмите кнопку**")
        price = st.sidebar.number_input("Цена покупки, %", value=price, min_value=5.0, max_value=300.0)
        com_pr = st.sidebar.number_input("Комиссия при покупке, %", value=0.04, min_value=0.0, max_value=1.0)
        use_offer = "Погашения"
        if offer_date != "":
            use_offer = st.sidebar.radio("Рассчитывать до даты",["Оферты","Погашения"])     
        use_nalog = st.sidebar.checkbox('Учитывать подоходный налог 13%', value=True)
        #st.sidebar.divider()
        st.sidebar.markdown('##')
        button1 = st.sidebar.button("Рассчитать доходность")
        if button1:
            #-----------  Получаем данные по купонам -------------------------------------
            ret, coup = fi.get_coups(sec_id)
            #-------------------------------------------------------------------------------------
            #coup.to_csv("c.csv",sep=";")   #-----  Выгрузка в файл для тестирования
            if mat_date == "":         
                st.error("У облигации отсутствует дата погашения. Расчет доходности невозможен !")            
            elif ret == -1:
                st.error("Не найдена таблица - календарь купонов по облигации. Расчет доходности не представляется возможным !")
            elif ret == 0:
                st.error("Таблица - календарь купонов по облигации - пуста. Расчет доходности не представляется возможным !")
            elif coup['amounts'][0]=="—":
                st.error("В таблице - календаре купонов нет сумм. Скорее всего, это облигация с плавающим купоном (флоутер). Расчет доходности не представляется возможным !")
            else:                
                #----  Номиналы
                nom_00 = float(nom_sum)   # Начальный
                nom_now = nom_00        # Текущий
                nom_prev = nom_now      # Предыдущий
                #---------   Вычисляем парамеры в нужном формате 
                f_buysum = round(nom_00*price/100,2)+round(float(nkd_sum),2)
                com_sum = round(f_buysum*com_pr/100,2) 
                if use_offer == 'Оферты':
                    f_s_enddate = offer_date
                else:
                    f_s_enddate = mat_date
                f_enddate = fi.get_next_work_day(f_s_enddate)
                #------------------------------------------------
                #----------  Немного улучшаем фрейм по купонам --
                #------------------------------------------------
                #---------  Фильтр - Оставляем только все данные по купонам до погашения или оферты и не раньше расчетной даты покупки 
                coup = coup[coup['s_dates'] >= f_s_buydate]              
                coup = coup[coup['s_dates'] <= f_s_enddate]              
                #------  Если суммы нет, то 0 (ноль)
                coup.loc[coup['amounts'] == "—", 'amounts'] = 0.00
                #------  Устанавливаем правильный тип поля  
                coup[['amounts']] = coup[['amounts']].astype(float)
                #------------------------------------------------
                #----------  Сохраняем в общий фрейм   ----------
                #------------------------------------------------    
                pl = coup[["dates","s_dates","amounts","comment"]].copy()    #-- оставляем только нужные поля    
                pl.reset_index(drop= True , inplace= True )     #-- сброс индекса      
                #--------  Если купон = 0, ту устанавливаем последний известный 
                amounts_prev = 0
                for index, row in pl.iterrows():
                    if row['amounts'] == 0:
                        pl['amounts'].loc[index] = amounts_prev
                        pl['comment'].loc[index] = "Купон(здесь=сумме последнего известного купона)"
                    else:
                        amounts_prev = row['amounts']     
                #---- Если купон не до даты погашения тела, то вычисляем 
                if len(pl.index)>0:
                    last_coup_date = pl['s_dates'].iloc[-1]  
                    if last_coup_date < f_s_enddate:    
                        part_sum = round(float(nom_sum)*float((f_s_enddate-last_coup_date).days)*float(coup_prc)/36500,2)
                        #pl.loc[len(pl.index)] = [f_enddate, f_s_enddate, part_sum,"Купон (часть)"]  
                        pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': part_sum,'comment': "Купон (часть)"}, index=[0])],ignore_index=True)                              
                #---------   Добавляем налог с купонов ---
                if use_nalog:
                    n = 0
                    for index,row in pl.iterrows():
                        if pl['amounts'][index] !=0:
                            n = n + 1
                            if n == 1:
                                #------ для 1-го купона база скорректирована на сумму НКД при покупке ---
                                pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 's_dates': pl['s_dates'][index],'amounts': round((pl['amounts'][index]-nkd_sum)*(-0.13),2),'comment': "Налог с суммы купона за вычетом НКД при покупке"}, index=[0])],ignore_index=True)                              
                            else:                            
                                pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 's_dates': pl['s_dates'][index],'amounts': round(pl['amounts'][index]*(-0.13),2),'comment': "Налог с суммы купона"}, index=[0])],ignore_index=True)                              
                #---------   Добавляем покупку  -----------
                #pl.to_csv("pl_.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #pl.loc[len(pl.index)] = [f_buydate, f_s_buydate, f_buysum*(-1),"Сумма сделки покупки, включая НКД"]
                pl = pd.concat([pl, pd.DataFrame({'dates': f_buydate, 's_dates': f_s_buydate,'amounts': f_buysum*(-1),'comment': "Сумма сделки покупки, включая НКД"}, index=[0])],ignore_index=True)                              
                #pl.to_csv("pl__.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #---------   Добавляем комиссию   -----------
                if com_sum>0:
                    #pl.loc[len(pl.index)] = [f_buydate, f_s_buydate, com_sum*(-1),"Комиссия при покупке"]
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_buydate, 's_dates': f_s_buydate,'amounts': com_sum*(-1),'comment': "Комиссия при покупке"}, index=[0])],ignore_index=True)                              
                #pl.to_csv("pl___.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #--------- Проверяем амортизации. Если есть , то заносим                 
                nnn = 0
                for index,row in coup.iterrows():
                    nnn = nnn + 1
                    if nnn>=2 and coup['prc'][index]>0:  # для второго купона
                        nm = round(coup['amounts'][index] * 36500 / coup['prc'][index] / float((coup['s_dates'][index]-s_date_prev).days),0)
                        if nm != "nan":
                            if nm < nom_prev:
                                s_dt = s_date_prev
                                dt = fi.get_next_work_day(s_dt)
                                asum = nom_prev - nm
                                if asum*100/nm > 3:    # больше 3-х %
                                    nom_now = nm
                                    #-------  Добавляем запись частичного погашения 
                                    #st.text(asum)
                                    #pl.loc[len(pl.index)] = [dt, s_dt, asum,"Частичное погашение тела облигации"]  
                                    pl = pd.concat([pl, pd.DataFrame({'dates': dt, 's_dates': s_dt,'amounts': asum,'comment': "Частичное погашение тела облигации"}, index=[0])],ignore_index=True)                              
                                    #------------------------------------------------------
                                    nom_prev = nom_now
                    s_date_prev = coup['s_dates'][index]
                #---------   Добавляем окончательное погашение -----
                #st.text("Последняя сумма -->" + str(nom_now))
                if nom_now>0:
                    #pl.loc[len(pl.index)] = [f_enddate,f_s_enddate,nom_now,"Погашение тела облигации"]
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': nom_now,'comment': "Погашение тела облигации"}, index=[0])],ignore_index=True)                              
                #--- если купили дешевле, то еще налог - в конце срока
                if use_nalog:
                    if (f_buysum + com_sum) < nom_00:
                        y_amount = (f_s_enddate - f_buydate).days//365    #-- число полных лет до погашения
                        if y_amount < 3:
                            pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': round((nom_sum-f_buysum-com_sum)*(-0.13),2),'comment': "Налог с разницы сумм погаш. и покупки с комиссией"}, index=[0])],ignore_index=True)     
                #st.dataframe(pl,800)                           
                #-------  Запуск расчета ------
                #pl2 = pl[["dates","amounts"]].copy() # 
                #pl[["dates","amounts"]].to_csv("2.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                IRR = xirr(pl[["dates","amounts"]])
                #st.divider()
                #-------  Только ненулевые суммы  
                rslt_pl = pl[pl['amounts'] != 0].copy() 
                #-------  Перерасчитываем дисконтируемые суммы потоков + добавляем столбец даты в нужном формате 
                rslt_pl['d_ams'] = 0
                rslt_pl['str_dates'] = ""
                rslt_pl['str_s_dates'] = ""
                dams_total = 0
                dur = 0
                #rslt_pl.to_csv("rslt_pl.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                for index, row in rslt_pl.iterrows():
                    rslt_pl['str_dates'].loc[index] = rslt_pl['dates'].loc[index].strftime("%d-%m-%Y")
                    rslt_pl['str_s_dates'].loc[index] = rslt_pl['s_dates'].loc[index].strftime("%d-%m-%Y")
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
                with col1: 
                    if IRR>0:
                        st.success("$$\Large\kern5cm Доходность: \space" + str(round(IRR*100,2)) + " \space\% $$")                
                    else:                    
                        st.error("$$\Large\kern5cm Доходность: \space" + str(round(IRR*100,2)) + " \space\% $$")                
                    #st.subheader("Доходность: " + str(round(IRR*100,2)) + " %")
                    if nom_cur != "SUR":
                        st.markdown("**Номинал облигации выражен в иностранной валюте " + nom_cur + ". При изменении курса валюты доходность также изменится." + "**")
                    if use_nalog and ((f_buysum+com_sum) < nom_00) and y_amount>=3:
                        st.markdown("**Длительность инвестиции будет составлять более 3-х лет. В этом случае применяется льгота долгосрочного владения (ЛДВ) и налог с разницы суммы погашения и суммы приобретения - не применяется." + "**")
                    st.markdown("**Дюрация Макколея: " + str(dur) + " лет**")
                    dur_m = round(dur/(1+IRR),1)
                    st.markdown("**Модифицированная дюрация: " + str(dur_m) + "**")
                    #-------  Сортируем и выводим подробности расчета 
                    #st.divider()
                with col2: 
                    st.markdown("##")    # пропуск строки
                    st.markdown("**Все денежные потоки**")    
                    #-------  Перерасчитываем дисконтируемые суммы потоков 
                    rslt_pl2 = rslt_pl.sort_values(by=['dates'])
                    rslt_pl2.reset_index(drop= True , inplace= True )     #-- сброс индекса  
                    rslt_pl3 = rslt_pl2[['str_dates','str_s_dates','comment','amounts','d_ams']]
                    rslt_pl3.columns = ['Дата потока','  Дата расч.','         Вид суммы', '  Сумма','Дисконтир.сумма']   #-- переименовать столбцы
                    nnn = rslt_pl3.shape[0]
                    if nnn>=26:
                        nnn = 26
                    st.dataframe(rslt_pl3, 1200, (nnn+1)*36) # Сначала ширина, потом - высота 
                #col1, col2 = st.columns([1,1.1])
                #with col2: 
                    st.markdown("**Итоговая сумма дисконтируемых денежных потоков:  " + str(round(dams_total,2)) + "**")
            #-----------------------------------------------------------------------------------------
#st.divider()
col1, col2 = st.columns([4,1])
with col2:    
    st.text("e-mail: tarasbmal@gmail.com")
