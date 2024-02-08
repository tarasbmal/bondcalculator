#---------------------------------------------------------------------------------------
#----   Функция получения SECID по параметру, который может быть  SECID,ISIN, Рег.Номеру
#----   а также, параллельно, остальных параметров с сайта Московской биржи
#---------------------------------------------------------------------------------------
def micex_get_sec(p_code):
	import pandas as pd
	import datetime 
	#-----   Выгружаем данные с сайта биржи в формате JSON -----
	url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?iss.only=securities'
	data = pd.read_json(url)
	#---- преобразуем данные в нормальный фрейм -----
	data = pd.DataFrame(data=data.iloc[1, 0], columns=data.iloc[0, 0])
	#-----  Фильтруем c условием ИЛИ ----
	res = data[(data["SECID"] == p_code) | (data["ISIN"] == p_code) | (data["REGNUMBER"] == p_code)]
	#ret = res['SECID'].max()
	if len(res.index)>0:
		#-- Код бумаги 
		sec_id = res['SECID'].iloc[0]
		#-- Наименование 
		sec_name = res['SECNAME'].iloc[0]
		#-- ISIN
		sec_isin = res['ISIN'].iloc[0]
		#-- Дата погашения
		mat_date = datetime.datetime.strptime(res['MATDATE'].iloc[0], "%Y-%m-%d").date()
		#-- Дата оферты 
		if len(str(res['OFFERDATE'].iloc[0]))>6:
			offer_date = datetime.datetime.strptime(res['OFFERDATE'].iloc[0], "%Y-%m-%d").date()
		else:
			#print(len(str(res['OFFERDATE'].iloc[0])))
			#print(res['OFFERDATE'].iloc[0])
			offer_date = ""						
		#-- Номинал
		nom_sum = res['FACEVALUE'].iloc[0]
		#-- Валюта номинала		
		nom_cur = res['FACEUNIT'].iloc[0]
		#-- Валюта расчетов (SUR- рубли)
		r_cur = res['CURRENCYID'].iloc[0]
		#-- Сумма купона
		coup_sum = res['COUPONVALUE'].iloc[0]
		#-----  Дата ближайшего купона
		coup_date = datetime.datetime.strptime(res['NEXTCOUPON'].iloc[0], "%Y-%m-%d").date()
		#-- % купона - нужно еще делить на 10000
		coup_prc = res['COUPONPERCENT'].iloc[0]
		#-- Период купона 
		coup_period = res['COUPONPERIOD'].iloc[0]
		#-- НКД (Внимание! Сумма НКД для замещающих облигаций, облигаций , номинированных в валюте - в рублях, т.е. нужно пересчитывать в валюту или просто посчитать НКД исходя из размера купона)
		nkd = res['ACCRUEDINT'].iloc[0]
		#-- Цена (предыдущая)
		price = res['PREVPRICE'].iloc[0]
		#-----------------------------------------------------------------------------
		#-- Если скорее всего, замещающая облигация, нужно пересчитывать НКД
		#-----------------------------------------------------------------------------
		if res['FACEUNIT'].iloc[0] != 'SUR' and  res['CURRENCYID'].iloc[0] == 'SUR':	
			#print("Замещающая облигация !!!")			
			#-----  Сегодня 
			buydate = datetime.datetime.today().date()
			#-----  Дней до купона
			days = (coup_date-buydate).days-1
			#-----  Осталось НКД до купона
			left_nkd = (res['FACEVALUE'].iloc[0] * res['COUPONPERCENT'].iloc[0] * days) / 36500
			#----- Расчетный НКД
			nkd = round(res['COUPONVALUE'].iloc[0] - left_nkd,2)	
			#print(nkd)
		#------------------------------------------------------
		#------------------------------------------------------
		#------------------------------------------------------
		ret = sec_id,sec_name,sec_isin,mat_date,offer_date,nom_sum,nom_cur,r_cur,coup_sum,coup_date,coup_prc,coup_period,nkd,price
	else:
		ret = "","","","","",0,"","",0,"",0,0,0,0
	return ret

#----------------------------------------------------------------------
#-------   Процедура получения данных по купонам с сайта smart-lab.ru
#----------------------------------------------------------------------
def get_coups(p_isin):
    import pandas as pd
    import datetime 
    import requests
    url = 'https://smart-lab.ru/q/bonds/' + p_isin
    hdr={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
    response = requests.get(url=url,stream=True, headers=hdr, verify=False)
    st_code = response.status_code
    if st_code != 200:
        return 0, ""    #-- облигация не найдена
    #-----   Купоны -----------------
    tabs = pd.read_html(response.text)
    df = tabs[0]
    coup = df[["Дата купона","Купон"]]  #-- Оставим только нужные колонки
    coup.columns = ["cd","amounts"] #-- переименуем столбцы
    coup["dates"] = datetime.date(2000,1,2)   #-- Новый столбец даты
    coup["comment"] = ""   #-- Комментарий
    for index,row in coup.iterrows():
        coup['dates'][index] = datetime.datetime.strptime(coup['cd'][index], "%d-%m-%Y").date()
        coup['comment'][index] = "Купон"
    coup = coup[["dates","amounts","comment"]]    #-- оставляем только нужные поля
    return 1, coup    #-- успешное завершение, облигация найдена
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
