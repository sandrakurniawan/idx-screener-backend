from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# Ini penting untuk Vercel agar frontend bisa mengakses backend Anda
app = FastAPI()

# Konfigurasi CORS (Cross-Origin Resource Sharing)
# Ganti "https://your-frontend-vercel-app.vercel.app" dengan URL frontend Vercel Anda yang sebenarnya
# Contoh: "https://nama-aplikasi-anda.vercel.app"
origins = [
    "http://localhost", # Untuk pengembangan lokal
    "http://localhost:3000", # Jika frontend Anda berjalan di port 3000 (misal React/Vue default)
    "http://localhost:5173", # Jika frontend Anda berjalan di port 5173 (misal Vite default)
    "https://idxscreener.vercel.app", # Ganti ini dengan domain Vercel Anda!
    "https://*.vercel.app" # Opsional: Izinkan semua subdomain Vercel Anda
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Mengizinkan semua metode HTTP (GET, POST, dll.)
    allow_headers=["*"], # Mengizinkan semua header
)

class IDXScreener:
    def __init__(self):
        # Common IDX stock symbols (you can expand this list)
        self.idx_symbols = [
            'BBCA.JK', 'TPIA.JK', 'BREN.JK', 'BYAN.JK', 'BBRI.JK',
            'BMRI.JK', 'AMMN.JK', 'DCII.JK', 'DSSA.JK', 'TLKM.JK',
            'ASII.JK', 'PANI.JK', 'BBNI.JK', 'DNET.JK', 'BRIS.JK',
            'ICBP.JK', 'CUAN.JK', 'BRPT.JK', 'AMRT.JK', 'SMMA.JK',
            'BNLI.JK', 'CPIN.JK', 'UNTR.JK', 'HMSP.JK', 'GOTO.JK',
            'ANTM.JK', 'INDF.JK', 'ISAT.JK', 'UNVR.JK', 'KLBF.JK',
            'ADRO.JK', 'GEMS.JK', 'AADI.JK', 'PGEO.JK', 'BELI.JK',
            'BRMS.JK', 'MTEL.JK', 'CASA.JK', 'MYOR.JK', 'SUPR.JK',
            'MDKA.JK', 'MLPT.JK', 'NCKL.JK', 'TBIG.JK', 'BNGA.JK',
            'ADMR.JK', 'BUMI.JK', 'PGAS.JK', 'MEGA.JK', 'MDIY.JK',
            'EXCL.JK', 'CMRY.JK', 'MBMA.JK', 'MIKA.JK', 'INCO.JK',
            'SRAJ.JK', 'MSIN.JK', 'INKP.JK', 'EMTK.JK', 'PTBA.JK',
            'CBDK.JK', 'PTRO.JK', 'NISP.JK', 'MEDC.JK', 'TCPI.JK',
            'PNBN.JK', 'TOWR.JK', 'SILO.JK', 'JSMR.JK', 'ARTO.JK',
            'AVIA.JK', 'BINA.JK', 'FILM.JK', 'AKRA.JK', 'ITMG.JK',
            'BDMN.JK', 'SRTG.JK', 'BTPN.JK', 'MKPI.JK', 'MAPI.JK',
            'HEAL.JK', 'PWON.JK', 'MPRO.JK', 'GGRM.JK', 'MAPA.JK',
            'JPFA.JK', 'TKIM.JK', 'INTP.JK', 'BSDE.JK', 'FAPA.JK',
            'SMGR.JK', 'TAPG.JK', 'CTRA.JK', 'BBTN.JK', 'BKSL.JK',
            'IMPC.JK', 'CITA.JK', 'MCOL.JK', 'RATU.JK', 'YUPI.JK',
            'BSIM.JK', 'BBHI.JK', 'CLEO.JK', 'SIDO.JK', 'MFIN.JK',
            'BNII.JK', 'CMNT.JK', 'BBSI.JK', 'STTP.JK', 'APIC.JK',
            'BUKA.JK', 'MIDI.JK', 'ULTJ.JK', 'BFIN.JK', 'GOOD.JK',
            'SSMS.JK', 'FASW.JK', 'MLBI.JK', 'LIFE.JK', 'JSPT.JK',
            'BANK.JK', 'CNMA.JK', 'BBKP.JK', 'TSPC.JK', 'POWR.JK',
            'AALI.JK', 'RISE.JK', 'BSSR.JK', 'NICL.JK', 'KPIG.JK',
            'SMSM.JK', 'RAJA.JK', 'HRUM.JK', 'SCMA.JK', 'ESSA.JK',
            'SMAR.JK', 'BTPS.JK', 'AUTO.JK', 'ACES.JK', 'MORA.JK',
            'PNLF.JK', 'INPP.JK', 'BJBR.JK', 'JRPT.JK', 'STAA.JK',
            'ARCI.JK', 'ALII.JK', 'ERAA.JK', 'PRAY.JK', 'ADMF.JK',
            'PLIN.JK', 'BMAS.JK', 'TINS.JK', 'ABMM.JK', 'BBMD.JK',
            'SOHO.JK', 'BJTM.JK', 'CMNP.JK', 'DAAZ.JK', 'LSIP.JK',
            'DSNG.JK', 'PSAB.JK', 'WIKA.JK', 'CARE.JK', 'EDGE.JK',
            'TMAS.JK', 'INDY.JK', 'TLDN.JK', 'DMND.JK', 'IBST.JK',
            'CYBR.JK', 'MTDL.JK', 'SMRA.JK', 'NSSS.JK', 'DUTI.JK',
            'SMCB.JK', 'DMAS.JK', 'EPMT.JK', 'POLU.JK', 'SIMP.JK',
            'LPKR.JK', 'DEWA.JK', 'NETV.JK', 'SMDM.JK', 'ADES.JK',
            'ANJT.JK', 'PALM.JK', 'TGKA.JK', 'SHIP.JK', 'BPII.JK',
            'AGRO.JK', 'SGER.JK', 'ENRG.JK', 'BSWD.JK', 'BNBR.JK',
            'NOBU.JK', 'BESS.JK', 'BIPI.JK', 'GIAA.JK', 'SDRA.JK',
            'FISH.JK', 'DRMA.JK', 'SMDR.JK', 'MPMX.JK', 'ROTI.JK',
            'SAME.JK', 'OMED.JK', 'BALI.JK', 'WIFI.JK', 'GOLF.JK',
            'MASB.JK', 'BIRD.JK', 'SSIA.JK', 'SGRO.JK', 'MSTI.JK',
            'ARNA.JK', 'TBLA.JK', 'LINK.JK', 'YULE.JK', 'HEXA.JK',
            'VICI.JK', 'HILL.JK', 'PBID.JK', 'CASS.JK', 'LPPF.JK',
            'GJTL.JK', 'PNIN.JK', 'MYOH.JK', 'JARR.JK', 'KIJA.JK',
            'RONY.JK', 'IMAS.JK', 'AGII.JK', 'TOBA.JK', 'SAMF.JK',
            'DOID.JK', 'TUGU.JK', 'MNCN.JK', 'CTBN.JK', 'PACK.JK',
            'VKTR.JK', 'INPC.JK', 'ELSA.JK', 'MMLP.JK', 'UNIC.JK',
            'RDTX.JK', 'KEJU.JK', 'SURE.JK', 'FORE.JK', 'PSGO.JK',
            'BBYB.JK', 'PGUN.JK', 'MTLA.JK', 'CENT.JK', 'KEEN.JK',
            'AGRS.JK', 'AMAR.JK', 'BCIC.JK', 'MARK.JK', 'BHAT.JK',
            'SMMT.JK', 'CBUT.JK', 'CPRO.JK', 'KAEF.JK', 'BNBA.JK',
            'BISI.JK', 'DMMX.JK', 'ASRI.JK', 'HRTA.JK', 'SKRN.JK',
            'GMTD.JK', 'KMTR.JK', 'MAHA.JK', 'NIRO.JK', 'DGWG.JK',
            'DAYA.JK', 'TOTL.JK', 'ASSA.JK', 'LPCK.JK', 'BOLT.JK',
            'MCOR.JK', 'BCAP.JK', 'PTPP.JK', 'KRAS.JK', 'TRIM.JK',
            'SFAN.JK', 'FMII.JK', 'TIFA.JK', 'BRAM.JK', 'ELPI.JK',
            'PYFA.JK', 'PRDA.JK', 'BACA.JK', 'MGRO.JK', 'MAPB.JK',
            'MBAP.JK', 'ARKO.JK', 'RALS.JK', 'SONA.JK', 'SMBR.JK',
            'DWGL.JK', 'CLAY.JK', 'TOTO.JK', 'TFCO.JK', 'BABP.JK',
            'BMTR.JK', 'GGRP.JK', 'WOOD.JK', 'BHIT.JK', 'PORT.JK',
            'GMFI.JK', 'UCID.JK', 'IFII.JK', 'RMKE.JK', 'MAYA.JK',
            'SMIL.JK', 'BUKK.JK', 'APLN.JK', 'VICO.JK', 'CSMI.JK',
            'BKSW.JK', 'BOGA.JK', 'DKFT.JK', 'TPMA.JK', 'ABDA.JK',
            'ISSP.JK', 'ADHI.JK', 'MBSS.JK', 'BMHS.JK', 'JAWA.JK',
            'NICE.JK', 'MINE.JK', 'ARGO.JK', 'DNAR.JK', 'SUNI.JK',
            'BGTG.JK', 'PNBS.JK', 'KKGI.JK', 'PSSI.JK', 'DATA.JK',
            'MTMH.JK', 'DVLA.JK', 'RAAM.JK', 'BEEF.JK', 'WIIM.JK',
            'MLIA.JK', 'HATM.JK', 'SPTO.JK', 'AMAG.JK', 'AMFG.JK',
            'BWPT.JK', 'IPCC.JK', 'SINI.JK', 'SCCO.JK', 'MSJA.JK',
            'DLTA.JK', 'BUAH.JK', 'BLES.JK', 'MAIN.JK', 'INDS.JK',
            'MLPL.JK', 'KINO.JK', 'IMJS.JK', 'IFSH.JK', 'LPGI.JK',
            'WINS.JK', 'PDPP.JK', 'BULL.JK', 'JTPE.JK', 'CSAP.JK',
            'MERK.JK', 'PMJS.JK', 'CEKA.JK', 'DEPO.JK', 'ACST.JK',
            'HERO.JK', 'JIHD.JK', 'BLTZ.JK', 'ENAK.JK', 'KBLI.JK',
            'UNIQ.JK', 'DILD.JK', 'IPCM.JK', 'ERAL.JK', 'INET.JK',
            'POLI.JK', 'PNGO.JK', 'SIPD.JK', 'IATA.JK', 'TRGU.JK',
            'INDR.JK', 'AREA.JK', 'TRST.JK', 'BBSS.JK', 'FAST.JK',
            'OMRE.JK', 'LTLS.JK', 'MKTR.JK', 'BVIC.JK', 'MCAS.JK',
            'BEKS.JK', 'BUVA.JK', 'CARS.JK', 'CSRA.JK', 'NFCX.JK',
            'BSBK.JK', 'ALDO.JK', 'CFIN.JK', 'KARW.JK', 'PPRO.JK',
            'AISA.JK', 'RSCH.JK', 'PTSN.JK', 'NEST.JK', 'TIRA.JK',
            'PBSA.JK', 'WOMF.JK', 'NATO.JK', 'ASGR.JK', 'JKON.JK',
            'AMOR.JK', 'IPTV.JK', 'SOCI.JK', 'IOTF.JK', 'SKLT.JK',
            'PANS.JK', 'AWAN.JK', 'BBLD.JK', 'CHIP.JK', 'CAMP.JK',
            'HGII.JK', 'ADCP.JK', 'BPFI.JK', 'FPNI.JK', 'PANR.JK',
            'BUDI.JK', 'ARII.JK', 'TCID.JK', 'GHON.JK', 'MFMI.JK',
            'BEST.JK', 'DEFI.JK', 'MDIA.JK', 'BABY.JK', 'HUMI.JK',
            'GWSA.JK', 'WIRG.JK', 'NELY.JK', 'ASLC.JK', 'ATIC.JK',
            'RSGK.JK', 'HOKI.JK', 'OASA.JK', 'ARTA.JK', 'PKPK.JK',
            'GDST.JK', 'CMPP.JK', 'SPMA.JK', 'SHID.JK', 'DOOH.JK',
            'VTNY.JK', 'MKAP.JK', 'RELI.JK', 'HITS.JK', 'NRCA.JK',
            'VOKS.JK', 'PTPW.JK', 'WSBP.JK', 'BIKE.JK', 'ITMA.JK',
            'APLI.JK', 'TEBE.JK', 'INDO.JK', 'IPOL.JK', 'PJAA.JK',
            'GSMF.JK', 'FORU.JK', 'BDKR.JK', 'GUNA.JK', 'KDSI.JK',
            'WTON.JK', 'AXIO.JK', 'UDNG.JK', 'IRRA.JK', 'ZONE.JK',
            'HDFA.JK', 'GRIA.JK', 'SMGA.JK', 'JECC.JK', 'GTSI.JK',
            'BRNA.JK', 'LIVE.JK', 'EKAD.JK', 'WINE.JK', 'RANC.JK',
            'STRK.JK', 'MPPA.JK', 'TBMS.JK', 'SQMI.JK', 'NAIK.JK'
        ]
        self.results_df = None

        # Parameters that will be set each run
        self.period = None
        self.interval = None
        self.consecutive_candles = None
        self.volume_multiplier = None

    def set_parameters(self, period, interval, consecutive_candles, volume_multiplier):
        """Set screening parameters"""
        self.period = period
        self.interval = interval
        self.consecutive_candles = consecutive_candles
        self.volume_multiplier = volume_multiplier

    def get_stock_data(self, symbol):
        """Get stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=self.period, interval=self.interval)
            if len(data) > 0:
                return symbol, data
            else:
                print(f"⚠️  No data available for {symbol}")
                return symbol, None
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return symbol, None

    def calculate_average_volume(self, data, lookback_periods=20):
        """Calculate average volume over lookback periods"""
        if len(data) < lookback_periods:
            return data['Volume'].mean()
        return data['Volume'].rolling(window=lookback_periods).mean()

    def check_consecutive_green_candles(self, data):
        """
        Check for consecutive green candles with proper rising pattern:
        - Each candle: Close > Open (green candle)
        - Each candle: Open >= Previous Close (no gap down)
        - This ensures true consecutive rising price pattern
        """
        num_candles = self.consecutive_candles

        if len(data) < num_candles:
            return False, None

        data = data.copy()

        # Calculate conditions for each candle
        data['is_green'] = data['Close'] > data['Open']  # Green candle condition
        data['prev_close'] = data['Close'].shift(1)      # Previous close price
        data['gap_up_or_equal'] = data['Open'] >= data['prev_close']  # No gap down condition

        # Combined condition: green candle AND no gap down
        data['valid_rising_candle'] = data['is_green'] & data['gap_up_or_equal']

        consecutive_count = 0
        results = []

        for i in range(1, len(data)):  # Start from index 1 (need previous close)
            if data['valid_rising_candle'].iloc[i]:
                consecutive_count += 1
                if consecutive_count >= num_candles:
                    # Found the pattern
                    start_idx = i - num_candles + 1
                    end_idx = i

                    # Calculate total price movement from start to end
                    total_rise = data['Close'].iloc[end_idx] - data['Open'].iloc[start_idx]
                    total_rise_pct = (total_rise / data['Open'].iloc[start_idx]) * 100

                    # Get individual candle details
                    candle_details = []
                    for j in range(start_idx, end_idx + 1):
                        candle_details.append({
                            'time': data.index[j].isoformat(), # Konversi datetime ke string ISO
                            'open': data['Open'].iloc[j],
                            'close': data['Close'].iloc[j],
                            'rise': data['Close'].iloc[j] - data['Open'].iloc[j],
                            'rise_pct': ((data['Close'].iloc[j] - data['Open'].iloc[j]) / data['Open'].iloc[j]) * 100
                        })

                    results.append({
                        'start_time': data.index[start_idx].isoformat(), # Konversi datetime ke string ISO
                        'end_time': data.index[end_idx].isoformat(),     # Konversi datetime ke string ISO
                        'start_price': data['Open'].iloc[start_idx],
                        'end_price': data['Close'].iloc[end_idx],
                        'total_price_change': total_rise,
                        'total_price_change_pct': total_rise_pct,
                        'candle_details': candle_details,
                        'pattern_strength': consecutive_count  # How many consecutive candles found
                    })
            else:
                consecutive_count = 0

        return len(results) > 0, results

    def check_volume_condition(self, data):
        """Check if current volume is more than X times average volume"""
        volume_multiplier = self.volume_multiplier
        avg_volume = self.calculate_average_volume(data)
        high_volume_periods = []

        for i in range(len(data)):
            if i < 20:  # Skip first 20 periods
                continue

            current_volume = data['Volume'].iloc[i]
            current_avg = avg_volume.iloc[i]

            if pd.notna(current_avg) and current_avg > 0 and current_volume > (current_avg * volume_multiplier):
                high_volume_periods.append({
                    'time': data.index[i].isoformat(), # Konversi datetime ke string ISO
                    'volume': current_volume,
                    'avg_volume': current_avg,
                    'volume_ratio': current_volume / current_avg
                })

        return len(high_volume_periods) > 0, high_volume_periods

    def screen_stock(self, symbol):
        """Screen individual stock for the criteria"""
        symbol_name, data = self.get_stock_data(symbol)

        if data is None or len(data) < 25:
            return None

        # Check for consecutive green candles with proper rising pattern
        has_green_pattern, green_results = self.check_consecutive_green_candles(data)

        # Check for high volume periods
        has_high_volume, volume_results = self.check_volume_condition(data)

        if has_green_pattern and has_high_volume:
            # Check if green pattern and high volume overlap
            matching_periods = []

            for green_period in green_results:
                for volume_period in volume_results:
                    # Convert volume_period['time'] to datetime object if it's string
                    volume_time_dt = datetime.fromisoformat(volume_period['time']) if isinstance(volume_period['time'], str) else volume_period['time']

                    # Check if volume spike occurs during the green candle pattern
                    if (datetime.fromisoformat(green_period['start_time']) <= volume_time_dt <=
                        datetime.fromisoformat(green_period['end_time']) + timedelta(minutes=2)): # Add timedelta for slight overlap tolerance
                        matching_periods.append({
                            'symbol': symbol_name,
                            'green_pattern': green_period,
                            'volume_spike': volume_period,
                            'current_price': data['Close'].iloc[-1],
                            'current_volume': data['Volume'].iloc[-1]
                        })

            if matching_periods:
                return {
                    'symbol': symbol_name,
                    'matches': matching_periods,
                    'total_matches': len(matching_periods)
                }

        return None

# Endpoint API untuk menjalankan screening
@app.post("/run_screening")
async def run_screening_api(
    period: str = "1d",
    interval: str = "1m",
    consecutive_candles: int = 4,
    volume_multiplier: float = 5.0
):
    screener = IDXScreener()
    screener.set_parameters(period, interval, consecutive_candles, volume_multiplier)

    results = []
    # Menggunakan ThreadPoolExecutor untuk paralelisme (sama seperti di notebook)
    with ThreadPoolExecutor(max_workers=5) as executor: # Sesuaikan max_workers jika perlu
        future_to_symbol = {
            executor.submit(screener.screen_stock, symbol): symbol
            for symbol in screener.idx_symbols
        }

        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {symbol}: {e}") # Log error di server

    if not results:
        return {"message": "No stocks found matching the criteria. Try adjusting parameters."}

    # Format hasil agar lebih rapi untuk respons API
    formatted_results = []
    for result in results:
        for match in result['matches']:
            green = match['green_pattern']
            volume = match['volume_spike']
            formatted_results.append({
                'Symbol': result['symbol'],
                'Pattern_Start_Time': green['start_time'],
                'Pattern_End_Time': green['end_time'],
                'Total_Rise_Percentage': round(green['total_price_change_pct'], 2),
                'Start_Price': int(green['start_price']),
                'End_Price': int(green['end_price']),
                'Volume_Ratio': round(volume['volume_ratio'], 1),
                'Current_Price': int(match['current_price']),
                'Volume_Spike_Time': volume['time']
            })
    return formatted_results

# Endpoint Root (opsional, untuk memastikan API berjalan)
@app.get("/")
async def read_root():
    return {"message": "IDX Stock Screener API is running!"}