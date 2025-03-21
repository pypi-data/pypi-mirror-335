<img src="Kronos.png"  width="100%">

*Python integration with Xautomata API*

# Kronos
Classe per la gestione dei timestamp in modo chiaro e univoco. La classe forza l'uso delle timezone indipendentemente da come
si crea l'oggetto temporale.

Kronos è basata sulla libreria standard di python **datetime** e su **pytz**.

Un oggetto Kronos è interamente compatibile con un oggetto datetime (che sia datetime.datetime, datetime.date, datetime.time).
Possono essere fatte operazioni incociate Kronos con datetime o isoformat. In ogni situazione Kronos convertira l'oggetto non Kronos per poi usarlo,
aggiungendo quindi la timezone se manca.

# utilizzo

## datetime / date / time

### creazione
il metodo **primetime** permette di creare un elemento temporale Kronos
```python
import Kronos
Kronos.primetime(year=2023, month=4)
>> 2023-04-01 00:00:00+00:00
```
**primetime** ha come campo obligatorio l'anno, i restanti valori vengono messi all'inizio del range temporale non assegnato.
Se non definita, di default viene impostata la timezone di UTC.

``Kronos.now()`` e ``Kronos.today()`` restituiscono l'oggetto Kronos rispettivamente con il momento corrente o 
il giorno corrente (la funzione ``Kronos.today()`` restituisce anche le ore e la timezone, semplicemente restituisce la data con l'ora fissata all'inizio del giorno).
Questo e' valido per ogni elemento che non sia un datetime, le date e i time vengono trasformati in datetime con timezone.

### conversione
E' possibile passare da datetime a Kronos e viceversa con semplici passaggi
```python
import Kronos
from datetime import datetime
now_k = Kronos.from_datetime(datetime.now())  # da datetime a kronos
now_dt = Kronos.now().datetime()  # da Kronos a datetime con funzione di estrazione
```

E' altrettanto semplice caricare convertire un isoformat in un oggetto kronos ``Kronos.from_iso('2023-01-01T00:00:00')``.

Un elemento Kronos è poi facilmente convertibile in un formato isoformat in piu di una maniera:
```python
import Kronos
now_iso1 = Kronos.now().iso()  # da Kronos a isoformat
now_iso2 = Kronos.now().isoformat()  # da Kronos a isoformat (identica alla precedente)
now_iso3 = Kronos.now().datetime().isoformat()  # da Kronos a datetime a isoformat()
```

In tutte queste situazioni, se la time zone è assente, **viene sempre automaticamente aggiunta e quella di default e' UTC**.

Se si carica un elemento **date** questo verra convertito in un **datetime** e abbianto ad una timezone.
Analogamente se si carica un elemento **time** questo verra convertito in **datetime** abbinando sempre la stessa data di 2000-10-10 
e in mancanza ti timezone verra assegnata pure quella, come si vede nel seguente esempio:

```python
import Kronos
Kronos.from_iso("12:00:00")  # da time in isoformat a kronos
>> 2000-10-10 12:00:00+00:00
```

### costruttori
- now
- today
- primetime
- from_isoformat
- from_iso
- from_timestamp
- from_ts
- from_datetime
- from_date
- from_dt (aka from_datetime)
- from_format
- from_list_iso_to_datetime
- from_list_iso
- from_timedelta
- from_td (aka from_timedelta)
- from_time

### funzioni
Esistono una serie di operazioni applicabili agli oggetti Kronos:
- start_of
- end_of
- add_duration
- subtract_duration
- ==, >, >=, <, <=, -
- date, datetime, isoformat, iso, timestamp, ts, time

Le operazioni ==, >, >=, <, <=, - permettono di confrontare date cross classi, permettendo di comparare stringhe in isoformat e datetime con Kronos, di seguito un esempio.
```python
import Kronos
from datetime import date, datetime
Kronos.now() > Kronos.from_iso("2022-01-01")  # Kronos con Kronos
>>> True
Kronos.now() > datetime.fromisoformat("2022-01-01")  # Kronos con datetime
>>> True
Kronos.now() > date.fromisoformat("2022-01-01")  # Kronos con date
>>> True
Kronos.now() > "2022-01-01"  # Kronos con stringa
>>> True
```

### start_of, end_of
Permettono di muovere il cursore temporale all'inizio o alla fine di una finestra scelta.
E' possibile sceglire di trasformare una data nell'inizio della giornata o nella fine della settimana, rispetto alla data selezionata.
```python
import Kronos
day = Kronos.now().start_of_day()  # ottengo l'inizio della giornata
month = Kronos.now().end_of_month()  # ottengo la fine del mese
```
I range temporale tra cui scegliere sono:
- minute
- hour
- day
- week
- month
- year

### add and subtract duration
Permette di aggiungere o togliere un certo ammontare di range temporale dalla data scelta.
```python
import Kronos
date = Kronos.from_iso('2023-01-01T00:00:00')  # converto un isoformat a Kronos
date.add_duration(days=3, minutes=7)  # aggiungo 3 giorni e 7 minuti
>> 2023-01-03 00:07:00+00:00
date.subtract_duration(years=1)  # tolgo 1 anno
>> 2022-01-01 00:00:00+00:00
```

### concatenazione
Tutte le operazioni applicabili su un elemento Kronos sono concatenabili
```python
import Kronos
date = Kronos.today().start_of_month().end_of_day().add_duration(hours=1)
```
Nell'esempio qui sopra viene presa la gioranta in formato date, viene preso l'inizio del mese e da li ci si sposta alla fine della giornata poi si aggiunge un ora.

### intervallo temporale
esiste un metodo leggermente differente, che dato un Kronos, un intervallo tempora e un offset restituisce gli estremi del range temporale richiesto.
```python
import Kronos
start, stop = Kronos.from_iso('2023-01-01T00:00:00').from_interval(10, 10, 'days')
>> 2022-12-11 00:00:00, 2022-12-21 00:00:00
```

## differenze temporali
Gli elementi Kronos supportano operazione di somma e sottrazione, ma a differenza di datetime, un operazione matematica tra due elementi kronos produce sempre un elemento kronos.
La ragione di questa scelta è legata al minimizzare gli import per fare operazioni su oggetti temporali.
Chiaramente una volta che un oggetto Kronos ha subito una operazione di questo genere non potra piu supportare i metodi indicati sopra.
Nonostante cio' supporta metodi analoghi a quelli di timedelta e si comportano in modo similare agli altri metodi di Kronos.

### +/-
Le operazioni supportate sono somme e sottrazioni
```python
import Kronos
now = Kronos.now()
yesterday = now.subtract_duration(days=1)
diff = now - yesterday
>> 1 days
```
Sottraendo due elementi Kronos si ottiene un oggetto differenza analogo in tutto e per tutto a un timedelta

### conversione
E' possibile passare da timedelta a Kronos e viceversa con semplici passatti
```python
import Kronos
from datetime import timedelta
now_k = Kronos.from_timedelta(td=timedelta(days=1))  # da timedelta a kronos
now_td = (Kronos.now() - Kronos.now().subtract_duration(days=1)).timedelta()  # da Kronos a timedelta
```

### approssimazione
gli oggetti Kronos di differenze temporali possono essere trasformati in numeri interi rappresentati l'approssimazione piu vicina al range temporale chiesto tramite il metodo ``in_periods``.
```python
import Kronos
now = Kronos.now()
yesterday = now.subtract_duration(days=1)
diff = now - yesterday
diff.in_days()
>> 1
```

## Timezones
Kronos possiede una libreria interna per la gestione delle Timezones.
La Timezone impostata di Default e' quella UTC, ma ogni volta che si crea un oggetto Kronos e' sempre possibile
aggiungere l'argomento *tz* per impostare una timezone diversa.

```python
import Kronos
Kronos.now('rome')
Kronos.primetime(2023, tz='rome')
```

Se l'elemento che si sta convertendo in Kronos gia possiede una timezone, quella impostata in aggiunta non verra usata.
Kronos si assicura che ogni suo elemento abbia una timezone, ma non si impone l'addove sia gia presente.

### Timezone adattiva
Sono presenti alcune nazioni di cui viene considerata la timezone rispetto al momento dell'anno modificandola in base
all'ora solare o legale.

```python
import Kronos
Kronos.primetime(2023, 12, 1, 0, 0, 0, 0, 'rome')
>> 2023-12-01 00:00:00+01:00
Kronos.primetime(2023, 8, 1, 0, 0, 0, 0, 'rome')
>> 2023-08-01 00:00:00+02:00
```

Al momento sono presenti:
- 'rome' (aka 'it' o 'IT')
- 'london' (aka 'uk' o 'UK')

### Timezone compatibile
In qualsiasi campo venga richiesta una timezone, puo essere inserito una qualsiasi oggetto time zone compatibile.
Possono essere usate direttamente le stringhe dello IANA time zone database, senza dover caricare la libreria pytz.
```python
import Kronos
from datetime import date, datetime, timedelta, time, timezone
from pytz import timezone as tz
Kronos.now(tz=timezone(timedelta(hours=1)))
>> 2024-07-24 13:35:26.653931+01:00
Kronos.now(tz=tz('US/Eastern'))
>> 2024-07-24 13:35:26.711635-04:56
Kronos.now(tz='US/Eastern')
>> 2024-07-24 13:35:26.711635-04:56
```

### Timezone generica
Le timezone intere sono gia codificate e sono richiamabili con semplici stringhe nel campo **tz**
```python
import Kronos
Kronos.now(tz='+01')
>> 2024-07-24 13:38:12.291010+01:00
Kronos.now(tz='-06')
>> 2024-07-24 13:38:12.292010-06:00
```

# Note utili

Offsets in Resample
```
Alias   Description

B       business day frequency
C       custom business day frequency
D       calendar day frequency
W       weekly frequency
ME      month end frequency
SME     semi-month end frequency (15th and end of month)
BME     business month end frequency
CBME    custom business month end frequency
MS      month start frequency
SMS     semi-month start frequency (1st and 15th)
BMS     business month start frequency
CBMS    custom business month start frequency
QE      quarter end frequency
BQE     business quarter end frequency
QS      quarter start frequency
BQS     business quarter start frequency
YE      year end frequency
BYE     business year end frequency
YS      year start frequency
BYS     business year start frequency
h       hourly frequency
bh      business hour frequency
cbh     custom business hour frequency
min     minutely frequency
s       secondly frequency
ms      milliseconds
us      microseconds
ns      nanoseconds
```