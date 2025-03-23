import smtplib

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe


class ModuloEmail(object):
	SERVER_GOOGLE_INVIO=('smtp.gmail.com',smtplib.SMTP_SSL_PORT)
	SERVER_VIRGILIO_INVIO=('out.virgilio.it',smtplib.SMTP_SSL_PORT)
	
	def __init__(self,credenzialiServer:tuple,isDebug:bool=False):
		self.credenzialiServer=credenzialiServer
		self.isDebug=isDebug
		self.connEmail=None
		self.utente=None
		self.isLogged=False
	
	def login(self,utente:str|None=None,password:str|None=None):
		if self.isLogged:
			return
		self.connEmail=smtplib.SMTP_SSL(*self.credenzialiServer)
		if self.isDebug:
			self.connEmail.set_debuglevel(1)
		# se serve setto l'autenticazione
		if utente is not None and password is not None:
			self.utente=utente
			self.connEmail.login(utente,password)
		self.isLogged=True
	
	def inviaEmail(self, mittente:str|None,destinatari, oggetto:str, messaggio:str,
			isHtml:bool, dataInvio=ModuloDate.now(), cc=None, ccn=None)->dict:
		# controllo i parametri
		dataInvio=ModuloDate.dateToString(dataInvio)
		if isinstance(destinatari, str):
			destinatari=[destinatari]
		if mittente is None:
			mittente=self.utente
		domain=self.utente.split("@")[-1]
		messageId=f"{ModuloDate.getSecs()}@{domain}"
		# creo il messaggio
		message=f"""Date: {dataInvio}
From: {mittente}
Subject: {oggetto}
To: {", ".join(destinatari)}
Message-ID: <{messageId}>
"""
		if not ModuloListe.isEmpty(cc):
			message+=("Cc: "+", ".join(cc))+"\n"
		if not ModuloListe.isEmpty(ccn):
			message+=("Bcc: "+", ".join(ccn))+"\n"
		message+="Content-Type: text/html;\n"
		# converto il messaggio in formato html
		if not isHtml:
			messaggio=ModuloStringhe.normalizzaEol(messaggio).replace("\n","<br/>\n")
		messaggio=messaggio.encode(ModuloStringhe.CODIFICA_ASCII,"xmlcharrefreplace").decode(ModuloStringhe.CODIFICA_UTF8)
		message+="\n"+messaggio
		# invio la mail
		try:
			return self.connEmail.sendmail(mittente,destinatari,message)
		except smtplib.SMTPServerDisconnected as ex:
			return {"":str(ex)}
	
	def close(self):
		if self.connEmail is None:
			return
		self.connEmail.quit()
		self.connEmail=None
		self.isLogged=False
