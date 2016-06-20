#encoding=UTF-8
import sys, httplib, time;
def hae_yksi_varaus(osoite,monistus):
	osoite=osoite.replace('https://','').replace('amp.jamk.fi','');#Poistetaan osoitteen alusta https:// mikäli se löytyy ja amp.jamk.fi jos löytyy
	print "Yhdistetään palvelimeen..."
	c = httplib.HTTPSConnection("amp.jamk.fi");#Otetaan yhteys palvelimeen
	c.request("GET", osoite);#Ja tehdään kysely osoitteella
	response = c.getresponse()
	if response.status!=200:#Jos palvelin antaa jonkun muun kuin 200 OK vastauksen niin keskeytetään
		print "VIRHE: "+str(response.status)+" "+response.reason;
		sys.exit("Haku ei onnistunut.")
	data = response.read().replace('\t','').split('\n');#Otetaan data ulos ja korvataan tabit pois sekä splitataan välilyöntien kohdalta
	kivat="";
	flip_1=False;
	flip_2=False;
	print "Sivu haettu, parsitaan tietoa...";
	for d in data:#Käydään rivi kerrallaan läpi
		if d.replace(' ','') == "<th>Opintojakso</th><th>Selite</th>":#Ensimmäinen stoppi
			flip_1=True;
		if flip_1 and d.replace(' ','') == "<trbgcolor=\"#e7e7e7\">":#Toinen stoppi
			flip_2=True;
		if flip_1 and flip_2:#Jos molemmat stopit on löydetty
			if d == "</table></td></tr></table></div>":#Jos löydetään loppustoppi
				break;
			kivat=kivat+d;#Kirjoitetaan rivi muuttujaan

	kivat=kivat.split('<tr  bgcolor="#e7e7e7" >');#Splitataan taulukoksi

	#
	#pvm=0;
	#aika=1;
	#tila=2;
	#ryhma=3;
	#opettaja=4;
	#kurssitunnus=5;
	#
	i=1;#Laskeminen alkaa riviltä yksi koska nolla on tyhjä rivi
	vevents="";
	olemassa=[];
	kurssitunnus="";
	while i<len(kivat):#Käydään kaikki rivit yksi kerrallaan läpi
		kirjoita=True
		#Poistetaan ylimääräinen roju ja splitataan rivi taulukoksi
		rivi=kivat[i].replace('<td>','').replace('</td></tr>','').replace('<font face="arial,verdana" size=-1>','').split('</td>');
		pvm=rivi[0].split(';')[1].split('.');#päivä=0, kuukausi=1, vuosi=3
		aika=rivi[1].replace(' - ',':').split(':');#alkutunti=0, alkumin=1,lopputunti=2, loppumin=3
		if not(monistus):#Jos käyttäjä ei ole poistanut monistusta käytöstä otetaan uid-lisä käyttöön
			lisa=str(i);
		else:
			lisa="";
		uid=rivi[5].replace(' ','_')+"@"+pvm[2]+pvm[1]+pvm[0]+"T"+aika[0]+aika[1]+"00"+lisa;#Tehdään uid kursitunnuksen, timestampin ja lisän perusteella
		if uid in olemassa:#Tarkistetaan ettei uid ole duplikaatti
			print "VIRHE: Kahdentunut UID "+uid+" - Ei kirjoiteta tiedostoon";
			kirjoita=False;#Laitetaan kirjoitus-flagi nolliin
		else:#Jos ei niin laitetaan tämä uid olemassa olevien taulukkoon
			olemassa.append(uid);
		if kirjoita:#Jos kirjoitus-flagi on true
			if len(kurssitunnus)<1:#Jos kurssitunnusta ei ole vielä kerrottu niin kerrotaan
				kurssitunnus=rivi[5];
			vevents=vevents+"BEGIN:VEVENT\r\n";
			vevents=vevents+"UID:"+uid+"\r\n";
			vevents=vevents+"DTSTAMP:"+time.strftime("%Y%m%d")+"T"+time.strftime("%H%M%S")+"\r\n";
			vevents=vevents+"DTSTART:"+pvm[2]+pvm[1]+pvm[0]+"T"+aika[0]+aika[1]+"00\r\n";
			vevents=vevents+"DTEND:"+pvm[2]+pvm[1]+pvm[0]+"T"+aika[2]+aika[3]+"00\r\n";
			vevents=vevents+"SUMMARY:"+rivi[5]+"\r\n";
			vevents=vevents+"LOCATION:"+rivi[2]+"\r\n";
			vevents=vevents+"DESCRIPTION:"+rivi[4]+"\r\n";
			vevents=vevents+"END:VEVENT\r\n";
		i=i+1;
	print "Löydettiin "+str(len(kivat))+" esiintymää";
	return [kurssitunnus,vevents.decode('iso-8859-1').encode('utf8')];#Palautetaan taulukkona ja UTF-8 koodattuna pääohjelmaan
